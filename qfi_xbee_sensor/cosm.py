# coding=utf8

import argparse
import ConfigParser
import csv
import json
import os
import requests
import sys
import time


class COSMService(object):
    base_url = 'http://api.cosm.com/v2'

    def __init__(self, ini_file):
        config = ConfigParser.ConfigParser()
        config.read(ini_file)
        self.api_key = config.get('cosm', 'apikey')
        self.user = config.get('cosm', 'user')
        self.data = {}
        self.feeds = None

    def add_row(self, timestamp, sensor, air, water):
        self.current_air = air
        self.current_water = water
        self.current_timestamp = timestamp
        data = self.data
        if sensor not in data:
            data[sensor] = sensor_data = {'air': [], 'water': []}
        else:
            sensor_data = data[sensor]
        sensor_data['air'].append((timestamp, air))
        sensor_data['water'].append((timestamp, water))

    def upload(self):
        for sensor, sensor_data in self.data.items():
            feed_url = self.get_feed_url(sensor)
            for temp in ('air', 'water'):
                url = feed_url + '/datastreams/%s/datapoints' % temp
                points = sensor_data[temp]
                while points:
                    batch = points[0:500]
                    post = json.dumps({'datapoints': [
                        {'at': format_timestamp(ts), 'value': value}
                        for ts, value in batch]})
                    headers = {'X-ApiKey': self.api_key,
                               'Content-Type': 'application/json',
                               'Content-Length': str(len(post))}
                    response = requests.post(url, data=post, headers=headers)
                    response.raise_for_status()
                    del points[0:500]

    def get_feed_url(self, sensor):
        feeds = self.get_feeds()
        title = 'qfi-mangroves-%s' % sensor
        if title not in feeds:
            url = self.create_feed(title)
        else:
            url = feeds[title]['feed']
        if url.endswith('.json'):
            url = url[:-5]
        return url

    def get_feeds(self):
        if self.feeds is None:
            url = self.base_url + '/feeds?user=%s' % self.user
            headers = {'X-ApiKey': self.api_key}
            self.feeds = dict([
                (feed['title'], feed) for feed in
                requests.get(url, headers=headers).json['results']])
        return self.feeds

    def create_feed(self, title):
        post = json.dumps({
            "title": title,
            "datastreams": [
                {"id": "air",
                 "unit":{"symbol":"°C","label":"DegC"},
                 "at": format_timestamp(self.current_timestamp),
                 "current_value": self.current_air},
                {"id": "water",
                 "unit":{"symbol":"°C","label":"DegC"},
                 "at": format_timestamp(self.current_timestamp),
                 "current_value": self.current_water}]
        })
        headers = {'X-ApiKey': self.api_key,
                   'Content-Type': 'application/json',
                   'Content-Length': str(len(post))}
        url = self.base_url + '/feeds'
        response = requests.post(url, data=post, headers=headers)
        response.raise_for_status()
        return response.headers['Location']


def upload_data(cosm, folder):
    pointer_file = os.path.join(folder, '.last_upload')
    files = [name for name in os.listdir(folder) if name.endswith('.csv')]
    files.sort()
    if os.path.exists(pointer_file):
        start_file, start_time = open(pointer_file).read().strip().split()
        start_time = float(start_time)
        while files[0] != start_file:
            files.pop(0)
    else:
        start_time = 0.0

    for fname in files:
        with open(os.path.join(folder, fname)) as f:
            reader = csv.reader(f)
            for timestamp, sensor, air, water in reader:
                timestamp = float(timestamp)
                if timestamp < start_time:
                    continue
                cosm.add_row(timestamp, sensor[8:], float(air), float(water))
    cosm.upload()

    with open(pointer_file, 'w') as f:
        print >> f, fname, timestamp


def format_timestamp(ts):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts))


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Upload sensor data to COSM")
    parser.add_argument('folder', metavar='FOLDER', help='Folder for data files.')
    parser.add_argument('ini_file', metavar='INI_FILE', help='Config ini file.')
    args = parser.parse_args(argv)

    upload_data(COSMService(args.ini_file), args.folder)
