import argparse
import csv
import os
import time
import sys

from collections import namedtuple
from pyramid.config import Configurator
from wsgiref.simple_server import make_server


SensorStatus = namedtuple('SensorStatus', ('id', 'timestamp', 'air', 'water'))


def application(folder):
    settings = {'folder': folder}
    config = Configurator(settings=settings)
    config.add_view(status_view, renderer='status.pt')
    return config.make_wsgi_app()


def status_view(request):
    folder = request.registry.settings.get('folder')
    datafiles = [name for name in os.listdir(folder) if name.endswith('.csv')]
    datafiles.sort()
    sensor_data = {}
    with open(os.path.join(folder, datafiles[-1])) as f:
        reader = csv.reader(f)
        for timestamp, sensor, air, water in reader:
            # Overwrite prev values, last one wins
            timestamp = time.asctime(time.localtime(float(timestamp)))
            sensor_data[sensor] = SensorStatus(
                sensor[-8:], timestamp, float(air), float(water))

    pointer_file = os.path.join(folder, '.last_upload')
    if os.path.exists(pointer_file):
        last_upload = open(pointer_file).read().strip().split()[1]
        last_upload = time.asctime(time.localtime(float(last_upload)))
    else:
        last_upload = None

    return {
        'sensor_data': sorted(sensor_data.values()),
        'last_upload': last_upload
    }


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Simple status web service.")
    parser.add_argument('folder', metavar='FOLDER',
                        help='Folder for data files.')
    args = parser.parse_args(argv)

    app = application(args.folder)
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
