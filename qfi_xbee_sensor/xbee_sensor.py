from xbee import ZigBee
from time import time
import argparse
import serial
import csv
import sys


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Continuously read sensor data from XBee and write to "
                    "data file.")
    parser.add_argument('-d', '--device', metavar='DEVICE',
                        default='/dev/ttyXBEE',
                        help='XBee serial device pseudofile')
    parser.add_argument('-b', '--baud', metavar='RATE', type=int, default=9600,
                        help='Baud rate of XBee serial device.')
    parser.add_argument('fname', metavar='FILE', help='Data file.')
    args = parser.parse_args(argv)

    ser = serial.Serial(args.device, args.baud)
    xbee = ZigBee(ser)

    # Continuously read and print packets
    while True:
        try:
            response = xbee.wait_read_frame()
            source_addr_long = response['source_addr_long'].encode("hex")
            with open(args.fname, 'a') as f:
                csvout = csv.writer(f)
                for sample in response['samples']:
                    row = [time(), source_addr_long,
                           sample['adc-0'], sample['adc-1']]
                    csvout.writerow(row)
        except KeyboardInterrupt:
            break

    ser.close()
