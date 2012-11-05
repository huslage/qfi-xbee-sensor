#!/usr/bin/python

from xbee import ZigBee
from time import time
import serial
import csv

ser = serial.Serial('/dev/tty.usbserial-A900XSAC', 9600)

xbee = ZigBee(ser)

# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        source_addr_long = response['source_addr_long'].encode("hex")
	with open('sensorlog.csv', 'a') as f:
            csvout = csv.writer(f)
	    for sample in response['samples']:
	        row = [time(), source_addr_long, sample['adc-0'], sample['adc-1']]
		csvout.writerow(row)
    except KeyboardInterrupt:
        break
        
ser.close()
