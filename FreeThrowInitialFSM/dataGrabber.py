from bluepy import btle
from bluepy.btle import Scanner, DefaultDelegate, ScanEntry, Peripheral
import struct
import time
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

# This is a delegate for receiving BTLE events


class BTEventHandler(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # Advertisement Data
        if isNewDev:
            print("Found new device:", dev.addr, dev.getScanData())

        # Scan Response
        if isNewData:
            print("Received more data", dev.addr, dev.getScanData())

    def handleNotification(self, cHandle, data):
        # Only print the value when the handle is 40 (the battery characteristic)
        # if cHandle == 40:
        #     print(data)
        #     print(struct.unpack('B', data))
        global numSamplesReceived
        global accelerationX
        global accelerationY
        global accelerationZ
        global velocityX
        global velocityY
        global velocityZ

        # Format of the data will be as follows:
        # a[0] => 0 means we are reading acceleration/velocity, 1 means angular velocity/angle
        # 1, 4, 7, 10, 13, 16 are sign bits
        # 2, 5, 8, 11, 14, 17 are the bits 8-15
        # 3, 6, 9, 12, 15, 18 are the bits 0-7
        if cHandle == 101:
            numSamplesReceived += 1
            recVals = struct.unpack('BBBBBBBBBBBBBBBBBBBB', data)
            print(struct.unpack('BBBBBBBBBBBBBBBBBBBB', data))

            val1 = (recVals[2] << 8) | recVals[3]
            val2 = (recVals[5] << 8) | recVals[6]
            val3 = (recVals[8] << 8) | recVals[9]
            val4 = (recVals[11] << 8) | recVals[12]
            val5 = (recVals[14] << 8) | recVals[15]
            val6 = (recVals[17] << 8) | recVals[18]
            # Reading Accel/velocity
            if recVals[0] == 0:
                accelerationX.append(
                    val1 if recVals[1]*val1 == 0 else (-1 * val1))
                accelerationY.append(
                    val2 if recVals[4]*val2 == 0 else (-1 * val2))
                accelerationZ.append(
                    val3 if recVals[7]*val3 == 0 else (-1 * val3))

                velocityX.append(
                    val4 if recVals[10]*val4 == 0 else (-1 * val4))
                velocityY.append(
                    val5 if recVals[13]*val5 == 0 else (-1 * val5))
                velocityZ.append(
                    val6 if recVals[16]*val6 == 0 else (-1 * val6))


handler = BTEventHandler()

# Create a scanner with the handler as delegate
scanner = Scanner().withDelegate(handler)

# Start scanning. While scanning, handleDiscovery will be called whenever a new device or new data is found
devs = scanner.scan(10)

# Get HEXIWEAR's address
hexi_addr = [dev for dev in devs if dev.getValueText(
    0x8) == 'HEXIWEAR'][0].addr

# Create a Peripheral object with the delegate
hexi = Peripheral().withDelegate(handler)

# Connect to Hexiwear
hexi.connect(hexi_addr)

# # Get the battery service
battery = hexi.getCharacteristics(uuid="2a19")[0]

# Get the client configuration descriptor and write 1 to it to enable notification
battery_desc = battery.getDescriptors(forUUID=0x2902)[0]
battery_desc.write(b"\x01", True)

alerts = hexi.getCharacteristics(uuid="2032")[0]
alerts_desc = alerts.getDescriptors(forUUID=0x2902)[0]
alerts_desc.write(b"\x01", True)


numSamplesReceived = 0
accelerationX = []
accelerationY = []
accelerationZ = []
velocityX = []
velocityY = []
velocityZ = []

# Infinite loop to receive notifications
while True:
    hexi.waitForNotifications(5.0)

    if numSamplesReceived >= 40:
        # Do some computation with the samples that are received
        print("Got 40 samples")

        # Convert to the full range -> so divide by 100 for all the terms:
        for i in range(0, 40):
            accelerationX[i] = float(accelerationX[i])/100.0
            accelerationY[i] = float(accelerationY[i])/100.0
            accelerationY[i] = float(accelerationY[i])/100.0
            velocityX[i] = float(velocityX[i])/100.0
            velocityY[i] = float(velocityY[i])/100.0
            velocityZ[i] = float(velocityZ[i])/100.0

        # Use some pre loaded machine learning model here to train and clasify the models!
        numSamplesReceived = 0
        time.sleep(5)
