from bluepy import btle
import bluepy.btle
from bluepy.btle import Scanner, DefaultDelegate, ScanEntry, Peripheral
import struct
import time
import numpy as np
from sklearn import linear_model

print("Done importing libraries.")

# Global Variables
numSamplesReceived = 0
elbowAccelerationX = []
elbowAccelerationY = []
elbowAccelerationZ = []
elbowAngleX = []
elbowAngleY = []
elbowAngleZ = []

wristAccelerationX = []
wristAccelerationY = []
wristAccelerationZ = []
wristAngleX = []
wristAngleY = []
wristAngleZ = []

shoulderAccelerationX = []
shoulderAccelerationY = []
shoulderAccelerationZ = []
shoulderAngleX = []
shoulderAngleY = []
shoulderAngleZ = []

timeArr = []
foundInitSequence = False

# Hexiwear Addresses
elbow_hexi_addr = '00:06:40:08:00:31' # '00:35:40:08:00:48'
wrist_hexi_addr = ''
shoulder_hexi_addr = ''


def try_until_success(func, exception=bluepy.btle.BTLEException, msg='reattempting', args=[]):
    retry = True
    while True:
        try:
            func(*args)
            retry = False
        except exception:
            print msg

        if not retry:
            break

# This is a delegate for receiving BTLE events
class ElbowBTEventHandler(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # Advertisement Data
        if isNewDev:
            pass
            # print("Found new device:", dev.addr, dev.getScanData())

        # Scan Response
        if isNewData:
            pass
            # print("Received more data", dev.addr, dev.getScanData())

    def handleNotification(self, cHandle, data):

        global elbowAccelerationX
        global elbowAccelerationY
        global elbowAccelerationZ
        global elbowAngleX
        global elbowAngleY
        global elbowAngleZ
        global timeArr
        global foundInitSequence

        # Format of the data will be as follows:
        # a[0] => 0 means we are reading acceleration/velocity, 1 means angular velocity/angle
        # 1, 4, 7, 10, 13, 16 are sign bits
        # 2, 5, 8, 11, 14, 17 are the bits 8-15
        # 3, 6, 9, 12, 15, 18 are the bits 0-7

        # Each iteration of this loop (all the appending) takes 0.006 seconds at max.
        # Thus that is what we should be using between sending the BLE signals at minimum!
        if cHandle == 101:
            # time1 = time.clock()
            recVals = struct.unpack('BBBBBBBBBBBBBBBBBBBB', data)
            print(struct.unpack('BBBBBBBBBBBBBBBBBBBB', data))

            val1 = (recVals[2] << 8) | recVals[3]
            val2 = (recVals[5] << 8) | recVals[6]
            val3 = (recVals[8] << 8) | recVals[9]
            val4 = (recVals[11] << 8) | recVals[12]
            val5 = (recVals[14] << 8) | recVals[15]
            val6 = (recVals[17] << 8) | recVals[18]
            index = recVals[19];

            # Reading Accel/velocity
            if recVals[0] == 0:
                if len(elbowAngleZ) < index:
                    elbowAccelerationX.append(val1 if recVals[1]*val1 == 0 else (-1 * val1))
                    elbowAccelerationY.append(val2 if recVals[4]*val2 == 0 else (-1 * val2))
                    elbowAccelerationZ.append(val3 if recVals[7]*val3 == 0 else (-1 * val3))

                    elbowAngleX.append(val4 if recVals[10]*val4 == 0 else (-1 * val4))
                    elbowAngleY.append(val5 if recVals[13]*val5 == 0 else (-1 * val5))
                    elbowAngleZ.append(val6 if recVals[16]*val6 == 0 else (-1 * val6))
            # timeArr.append(time.clock() - time1)

            # This means that the wrist has gotten the start motion signal and we should now send the
            if recVals[0] == 3:
                foundInitSequence = True

'''
class WristBTEventHandler(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # Advertisement Data
        if isNewDev:
            # print("Found new device:", dev.addr, dev.getScanData())

        # Scan Response
        if isNewData:
            # print("Received more data", dev.addr, dev.getScanData())

    def handleNotification(self, cHandle, data):

        global wristAccelerationX
        global wristAccelerationY
        global wristAccelerationZ
        global wristAngleX
        global wristAngleY
        global wristAngleZ
        global foundInitSequence

        # Format of the data will be as follows:
        # a[0] => 0 means we are reading acceleration/velocity, 1 means angular velocity/angle
        # 1, 4, 7, 10, 13, 16 are sign bits
        # 2, 5, 8, 11, 14, 17 are the bits 8-15
        # 3, 6, 9, 12, 15, 18 are the bits 0-7

        # Each iteration of this loop (all the appending) takes 0.006 seconds at max.
        # Thus that is what we should be using between sending the BLE signals at minimum!
        if cHandle == 101:
            recVals = struct.unpack('BBBBBBBBBBBBBBBBBBBB', data)
            print(struct.unpack('BBBBBBBBBBBBBBBBBBBB', data))

            val1 = (recVals[2] << 8) | recVals[3]
            val2 = (recVals[5] << 8) | recVals[6]
            val3 = (recVals[8] << 8) | recVals[9]
            val4 = (recVals[11] << 8) | recVals[12]
            val5 = (recVals[14] << 8) | recVals[15]
            val6 = (recVals[17] << 8) | recVals[18]
            index = recVals[19];

            # Reading Accel/velocity
            if recVals[0] == 0:
                if len(elbowAngleZ) < index:
                    wristAccelerationX.append(val1 if recVals[1]*val1 == 0 else (-1 * val1))
                    wristAccelerationY.append(val2 if recVals[4]*val2 == 0 else (-1 * val2))
                    wristAccelerationZ.append(val3 if recVals[7]*val3 == 0 else (-1 * val3))

                    wristAngleX.append(val4 if recVals[10]*val4 == 0 else (-1 * val4))
                    wristAngleY.append(val5 if recVals[13]*val5 == 0 else (-1 * val5))
                    wristAngleZ.append(val6 if recVals[16]*val6 == 0 else (-1 * val6))

            # This means that the wrist has gotten the start motion signal and we should now send the
            if recVals[0] == 3:
                foundInitSequence = True
'''


print("Adding the handler")
elbow_handler = ElbowBTEventHandler()
print("Creating a scanner.")
# Create a scanner with the handler as delegate
scanner = Scanner().withDelegate(elbow_handler)
# Start scanning. While scanning, handleDiscovery will be called whenever a new device or new data is found
devs = scanner.scan(10)
# Get HEXIWEAR's address
# Create a Peripheral object with the delegate
elbow_hexi = Peripheral().withDelegate(elbow_handler)

print("Trying to connect")
# Connect to Hexiwear
# elbow_hexi.connect(elbow_hexi_addr)
try_until_success(elbow_hexi.connect, msg='error connecting to 1',
                  args=[elbow_hexi_addr])

print("Connected to device!")
# Get the battery service
battery = elbow_hexi.getCharacteristics(uuid="2a19")[0]
# Get the client configuration descriptor and write 1 to it to enable notification
battery_desc = battery.getDescriptors(forUUID=0x2902)[0]
battery_desc.write(b"\x01", True)

alerts = elbow_hexi.getCharacteristics(uuid="2032")[0]
alerts_desc = alerts.getDescriptors(forUUID=0x2902)[0]
alerts_desc.write(b"\x01", True)

connectCommand = '11111111111111111111'
collectCommand = '22222222222222222222'
# After all of the hexi's have been connected, then we should send this this:
alertConnection = elbow_hexi.getCharacteristics(uuid="2031")[0]
# alertConnection.write(connectCommand, True)
try_until_success(alertConnection.write, msg='Error sending connection command', args=[connectCommand, True])

# Infinite loop to receive notifications
while True:
    elbow_hexi.waitForNotifications(5.0)

    if foundInitSequence:
        # Repeat this for all three Hexiwears
        # alertConnection.write(collectCommand, True)
        try_until_success(alertConnection.write, msg='Error sending collection command', args=[collectCommand, True])

        # stop sending collection command after a success
        foundInitSequence = False

    if len(elbowAngleZ) >= 50:
        # Do some computation with the samples that are received
        print("Got 50 samples")
        # Convert to the full range -> so divide by 100 for all the terms:
        for i in range(0, 50):
            elbowAccelerationX[i] = float(elbowAccelerationX[i])/100.0
            elbowAccelerationY[i] = float(elbowAccelerationY[i])/100.0
            elbowAccelerationZ[i] = float(elbowAccelerationZ[i])/100.0
            elbowAngleX[i] = float(elbowAngleX[i])/100.0
            elbowAngleY[i] = float(elbowAngleY[i])/100.0
            elbowAngleZ[i] = float(elbowAngleZ[i])/100.0

        # Use some pre loaded machine learning model here to train and clasify the models!
        numSamplesReceived = 0
        elbowAccelerationX = []
        elbowAccelerationY = []
        elbowAccelerationZ = []

        elbowAngleX = []
        elbowAngleY = []
        elbowAngleZ = []
        time.sleep(10)
