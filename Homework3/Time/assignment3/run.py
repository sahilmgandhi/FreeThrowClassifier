#!/usr/bin/python

import bluepy.btle
from bluepy.btle import Scanner, DefaultDelegate, ScanEntry, Peripheral
import struct
import time
from datetime import datetime

f = open("mac.txt", "r")
hexiOneAddress = str(f.readline().rstrip())
print(hexiOneAddress)
hexiTwoAddress = str(f.readline().rstrip())
print(hexiTwoAddress)


def try_send_until_success(func, hexi_num,  exception=bluepy.btle.BTLEException, msg='reattempting'):
    retry = True
    while True:
        timeCommand = str(datetime.now().strftime('%H:%M:%S.%f')) + 'aaaaa'
        #print(hexi_num + timeCommand)
        args = [timeCommand, True]
        try:
            func(*args)
            retry = False
        except exception:
            print msg

        if not retry:
            break


def try_add_until_success(func, exception=bluepy.btle.BTLEException, msg='reattempting', args=[]):
    retry = True
    while True:
        try:
            func(*args)
            retry = False
        except exception:
            print msg
        if not retry:
            break


hexiOne = Peripheral()
hexiTwo = Peripheral()

print("Connecting to the first hexiwear")
try_add_until_success(hexiOne.connect, msg='error connecting to 1',
                      args=[hexiOneAddress])

print("Connecting to the second hexiwear")
try_add_until_success(hexiTwo.connect, msg='error connecting to 2',
                      args=[hexiTwoAddress])

print("Done connecting")
timeControl = hexiOne.getCharacteristics(uuid='2031')[0]  # Alert Input
timeTwoControl = hexiTwo.getCharacteristics(uuid='2031')[0]  # Alert Input

#try_send_until_success(timeControl.write, "Hexi One: ",msg='Error sending time to the first one')
#try_send_until_success(timeTwoControl.write, "Hexi Two: ", msg='Error sending the time to the second one')

count = 30

while True:
    if count >= 30:
        try_send_until_success(timeTwoControl.write, "Hexi Two: ",
                               msg='Error sending the time to the second one')
        try_send_until_success(
            timeControl.write, "Hexi One: ", msg='Error sending time to the first one')
        count = 0
    print(str(datetime.now().strftime('%H:%M:%S.%f')))
    time.sleep(1)
    count = count + 1
