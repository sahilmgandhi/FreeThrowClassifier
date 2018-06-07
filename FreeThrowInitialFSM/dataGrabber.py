from bluepy import btle
from bluepy.btle import Scanner, DefaultDelegate, ScanEntry, Peripheral
import struct

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
        #     print(struct.unpack('B', data))
        global numSamplesReceived
        if cHandle == 101:
            numSamplesReceived += 1
            print(data)


numSamplesReceived = 0

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


# Infinite loop to receive notifications
while True:
    hexi.waitForNotifications(480.0)

    if numSamplesReceived == 40:
        # Do some computation with the samples that are received
        numSamplesReceived = 0
        pass
