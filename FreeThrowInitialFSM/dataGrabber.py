from bluepy import btle
import bluepy.btle
from bluepy.btle import Scanner, DefaultDelegate, ScanEntry, Peripheral
import struct
import time
import numpy as np
from sklearn import linear_model
import pickle

print("Done importing libraries.")

print("Importing ML Models")

wristModels = []
elbowModels = []
shoulderModels = []

indices = np.arange(0.01, 5.01, 0.1)
for i in indices:
    currElbowFile = 'elbow{0:.2f}.sav'.format(i)
    currWristFile = 'wrist{0:.2f}.sav'.format(i)
    currShoulderFile = 'shoulder{0:.2f}.sav'.format(i)

    wristModels.append(pickle.load(open(currWristFile, 'rb')))
    elbowModels.append(pickle.load(open(currElbowFile, 'rb')))
    shoulderModels.append(pickle.load(open(currShoulderFile, 'rb')))


# Global Variables
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
elbow_hexi_addr = '00:35:40:08:00:48'
wrist_hexi_addr = '00:06:40:08:00:31'
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

# This is a delegate for receiving BTLE events for the Elbow


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

            val1 = (recVals[2] * 256) + recVals[3]
            val2 = (recVals[5] * 256) + recVals[6]
            val3 = (recVals[8] * 256) + recVals[9]
            val4 = (recVals[11] * 256) + recVals[12]
            val5 = (recVals[14] * 256) + recVals[15]
            val6 = (recVals[17] * 256) + recVals[18]
            index = recVals[19]

            # Reading Accel/velocity
            if recVals[0] == 0:
                if len(elbowAngleZ) < index:
                    elbowAngleX.append(
                        val1 if recVals[1]*val1 == 0 else (-1 * val1))
                    elbowAngleY.append(
                        val2 if recVals[4]*val2 == 0 else (-1 * val2))
                    elbowAngleZ.append(
                        val3 if recVals[7]*val3 == 0 else (-1 * val3))

                    elbowAccelerationX.append(
                        val4 if recVals[10]*val4 == 0 else (-1 * val4))
                    elbowAccelerationY.append(
                        val5 if recVals[13]*val5 == 0 else (-1 * val5))
                    elbowAccelerationZ.append(
                        val6 if recVals[16]*val6 == 0 else (-1 * val6))
            # timeArr.append(time.clock() - time1)

# This is a delegate for receiving BTLE events for the wrist


class WristBTEventHandler(DefaultDelegate):
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

            val1 = (recVals[2] * 256) + recVals[3]
            val2 = (recVals[5] * 256) + recVals[6]
            val3 = (recVals[8] * 256) + recVals[9]
            val4 = (recVals[11] * 256) + recVals[12]
            val5 = (recVals[14] * 256) + recVals[15]
            val6 = (recVals[17] * 256) + recVals[18]
            index = recVals[19]

            # Reading Accel/velocity
            if recVals[0] == 0:
                if len(elbowAngleZ) < index:
                    wristAngleX.append(
                        val1 if recVals[1]*val1 == 0 else (-1 * val1))
                    wristAngleY.append(
                        val2 if recVals[4]*val2 == 0 else (-1 * val2))
                    wristAngleZ.append(
                        val3 if recVals[7]*val3 == 0 else (-1 * val3))

                    wristAccelerationX.append(
                        val4 if recVals[10]*val4 == 0 else (-1 * val4))
                    wristAccelerationY.append(
                        val5 if recVals[13]*val5 == 0 else (-1 * val5))
                    wristAccelerationZ.append(
                        val6 if recVals[16]*val6 == 0 else (-1 * val6))

            # This means that the wrist has gotten the start motion signal and we should now send the
            if recVals[0] == 3:
                foundInitSequence = True

# This is a delegate for receiving BTLE events for the Shoulder


class ShoulderBTEventHandler(DefaultDelegate):
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

        global shoulderAccelerationX
        global shoulderAccelerationY
        global shoulderAccelerationZ
        global shoulderAngleX
        global shoulderAngleY
        global shoulderAngleZ

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

            val1 = (recVals[2] * 256) + recVals[3]
            val2 = (recVals[5] * 256) + recVals[6]
            val3 = (recVals[8] * 256) + recVals[9]
            val4 = (recVals[11] * 256) + recVals[12]
            val5 = (recVals[14] * 256) + recVals[15]
            val6 = (recVals[17] * 256) + recVals[18]
            index = recVals[19]

            # Reading Accel/velocity
            if recVals[0] == 0:
                if len(elbowAngleZ) < index:
                    shoulderAngleX.append(
                        val1 if recVals[1]*val1 == 0 else (-1 * val1))
                    shoulderAngleY.append(
                        val2 if recVals[4]*val2 == 0 else (-1 * val2))
                    shoulderAngleZ.append(
                        val3 if recVals[7]*val3 == 0 else (-1 * val3))

                    shoulderAccelerationX.append(
                        val4 if recVals[10]*val4 == 0 else (-1 * val4))
                    shoulderAccelerationY.append(
                        val5 if recVals[13]*val5 == 0 else (-1 * val5))
                    shoulderAccelerationZ.append(
                        val6 if recVals[16]*val6 == 0 else (-1 * val6))

            # This means that the wrist has gotten the start motion signal and we should now send the
            if recVals[0] == 3:
                foundInitSequence = True


print("Adding the handler")
elbow_handler = ElbowBTEventHandler()
shoulder_handler = ShoulderBTEventHandler()
wrist_handler = WristBTEventHandler()

# print("Creating a scanner.")
# Create a scanner with the handler as delegate
# scanner = Scanner().withDelegate(elbow_handler)
# Start scanning. While scanning, handleDiscovery will be called whenever a new device or new data is found
# devs = scanner.scan(10)

# Create a Peripheral object with the delegate
wrist_hexi = Peripheral().withDelegate(wrist_handler)
elbow_hexi = Peripheral().withDelegate(elbow_handler)
shoulder_hexi = Peripheral().withDelegate(shoulder_handler)


print("Trying to connect")
# Connect to Hexiwear
try_until_success(wrist_hexi.connect,
                  msg='error connecting to wrist', args=[wrist_hexi_addr])
try_until_success(elbow_hexi.connect, msg='error connecting to elbow',
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

# Get the battery service
battery2 = wrist_hexi.getCharacteristics(uuid="2a19")[0]
# Get the client configuration descriptor and write 1 to it to enable notification
battery_desc2 = battery2.getDescriptors(forUUID=0x2902)[0]
battery_desc2.write(b"\x01", True)

alerts2 = wrist_hexi.getCharacteristics(uuid="2032")[0]
alerts_desc2 = alerts2.getDescriptors(forUUID=0x2902)[0]
alerts_desc2.write(b"\x01", True)

connectCommand = '11111111111111111111'
collectCommand = '22222222222222222222'
# After all of the hexi's have been connected, then we should send this this:
alertConnection = elbow_hexi.getCharacteristics(uuid="2031")[0]
alertConnection2 = wrist_hexi.getCharacteristics(uuid="2031")[0]
try_until_success(alertConnection.write,
                  msg='Error sending connection command', args=[connectCommand, True])
try_until_success(alertConnection2.write,
                  msg='Error sending connection command', args=[connectCommand, True])

# Infinite loop to receive notifications
while True:
    elbow_hexi.waitForNotifications(5.0)

    if foundInitSequence:
        # Repeat this for all three Hexiwears
        # alertConnection.write(collectCommand, True)
        try_until_success(alertConnection.write, msg='Error sending collection command', args=[
                          collectCommand, True])
        try_until_success(alertConnection2.write, msg='Error sending collection command', args=[
                          collectCommand, True])

        # stop sending collection command after a success
        foundInitSequence = False

    if len(elbowAngleZ) >= 50 and len(wristAngleZ) >= 50:
        # if len(elbowAngleZ) >= 50 and len(shoulderAngleZ) >= 50 and len(wristAngleZ) >= 50:
        # Do some computation with the samples that are received
        print("Got 50 samples")
        fullWristModel = []
        fullElbowModel = []
        fullShoulderModel = []

        # Convert to the full range -> so divide by 100 for all the terms:
        for i in range(0, 50):
            elbowAccelerationX[i] = float(elbowAccelerationX[i])/100.0
            elbowAccelerationY[i] = float(elbowAccelerationY[i])/100.0
            elbowAccelerationZ[i] = float(elbowAccelerationZ[i])/100.0
            elbowAngleX[i] = float(elbowAngleX[i])/100.0
            elbowAngleY[i] = float(elbowAngleY[i])/100.0
            elbowAngleZ[i] = float(elbowAngleZ[i])/100.0

            wristAccelerationX[i] = float(wristAccelerationX[i])/100.0
            wristAccelerationY[i] = float(wristAccelerationY[i])/100.0
            wristAccelerationZ[i] = float(wristAccelerationZ[i])/100.0
            wristAngleX[i] = float(wristAngleX[i])/100.0
            wristAngleY[i] = float(wristAngleY[i])/100.0
            wristAngleZ[i] = float(wristAngleZ[i])/100.0

            shoulderAccelerationX[i] = float(shoulderAccelerationX[i])/100.0
            shoulderAccelerationY[i] = float(shoulderAccelerationY[i])/100.0
            shoulderAccelerationZ[i] = float(shoulderAccelerationZ[i])/100.0
            shoulderAngleX[i] = float(shoulderAngleX[i])/100.0
            shoulderAngleY[i] = float(shoulderAngleY[i])/100.0
            shoulderAngleZ[i] = float(shoulderAngleZ[i])/100.0

            currWristRow = []
            currWristRow.append(elbowAngleX[i])
            currWristRow.append(elbowAngleY[i])
            currWristRow.append(elbowAngleZ[i])
            currWristRow.append(elbowAccelerationX[i])
            currWristRow.append(elbowAccelerationY[i])
            currWristRow.append(elbowAccelerationZ[i])
            fullWristModel.append(currWristRow)

            currShoulderRow = []
            currShoulderRow.append(elbowAngleX[i])
            currShoulderRow.append(elbowAngleY[i])
            currShoulderRow.append(elbowAngleZ[i])
            currShoulderRow.append(elbowAccelerationX[i])
            currShoulderRow.append(elbowAccelerationY[i])
            currShoulderRow.append(elbowAccelerationZ[i])
            fullShoulderModel.append(currShoulderRow)

            currElbowRow = []
            currElbowRow.append(elbowAngleX[i])
            currElbowRow.append(elbowAngleY[i])
            currElbowRow.append(elbowAngleZ[i])
            currElbowRow.append(elbowAccelerationX[i])
            currElbowRow.append(elbowAccelerationY[i])
            currElbowRow.append(elbowAccelerationZ[i])
            fullElbowModel.append(currElbowRow)

        # Ml Model wants angleX, angleY, angleZ, accelX, accelY, accelZ in one array:
        wristAccuracy = []
        shoulderAccuracy = []
        elbowAccuracy = []
        for i in range(5, 35):
            currModel = np.array(fullWristModel[i]).reshape(1, -1)
            wristAccuracy.append(wristModels[i].predict(currModel))

            currModel = np.array(fullElbowModel[i]).reshape(1, -1)
            elbowAccuracy.append(elbowModels[i].predict(currModel))

            currModel = np.array(fullShoulderModel[i]).reshape(1, -1)
            shoulderAccuracy.append(shoulderModels[i].predict(currModel))

        print(np.average(wristAccuracy))
        if np.average(wristAccuracy) > 0.5:
            print("It is a good shot")
        else:
            print("It is a bad shot")

        # Use some pre loaded machine learning model here to train and clasify the models!
        elbowAccelerationX = []
        elbowAccelerationY = []
        elbowAccelerationZ = []
        elbowAngleX = []
        elbowAngleY = []
        elbowAngleZ = []

        shoulderAccelerationX = []
        shoulderAccelerationY = []
        shoulderAccelerationZ = []
        shoulderAngleX = []
        shoulderAngleY = []
        shoulderAngleZ = []

        wristAccelerationX = []
        wristAccelerationY = []
        wristAccelerationZ = []
        wristAngleX = []
        wristAngleY = []
        wristAngleZ = []

        time.sleep(10)
