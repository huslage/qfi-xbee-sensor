import argparse
import csv
import datetime
import os
import serial
import sys

from time import time
from xbee import ZigBee


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Continuously read sensor data from XBee and write to "
                    "data files in specified folder.")
    parser.add_argument('-d', '--device', metavar='DEVICE',
                        default='/dev/ttyXBEE',
                        help='XBee serial device pseudofile')
    parser.add_argument('-b', '--baud', metavar='RATE', type=int, default=9600,
                        help='Baud rate of XBee serial device.')
    parser.add_argument('folder', metavar='FOLDER', help='Folder for data files.')
    args = parser.parse_args(argv)

    ser = serial.Serial(args.device, args.baud)
    xbee = ZigBee(ser)

    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    # Continuously read and print packets
    while True:
        try:
            today = datetime.date.today()
            fname = '%4d-%02d-%02d.csv' % (today.year, today.month, today.day)
            response = xbee.wait_read_frame()
            source_addr_long = response['source_addr_long'].encode("hex")
            with open(os.path.join(args.folder, fname), 'a') as f:
                csvout = csv.writer(f)
                for sample in response['samples']:
                    row = (time(), source_addr_long,
                           temp(sample['adc-0']), temp(sample['adc-1']))
                    csvout.writerow(row)
        except KeyboardInterrupt:
            break

    ser.close()


def temp(sample):
    """
    Convert an integer sample from an A->D converter into a temperature reading.
    """
    # XXX ???
    return sample
