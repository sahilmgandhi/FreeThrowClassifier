# The publisher must connect to the hexiwear and listen in for the button presses
# When it gets the button press, depending on what it is, it should publish!

import pip
import paho.mqtt.client as mqtt
import bluepy.btle
from bluepy.btle import Scanner, DefaultDelegate, ScanEntry, Peripheral
import struct

macFile = open("mac.txt", "r")
hexiOneAddress = str(macFile.readline().rstrip())
print(hexiOneAddress)
macFile.close()

# callback function for connection


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Broker connection successful")
    else:
        print("Error connecting to broker")


# broker to connect to
broker = "broker.hivemq.com"

topic = "ecem119/2018s/hexiwear/" + hexiOneAddress

# define events to publish
up = "event up"
down = "event down"
left = "event left"
right = "event right"

print("Creating new instance")
client = mqtt.Client()
client.on_connect = on_connect

client.connect(broker)  # connect to broker
client.loop_start()  # start the loop
print("Subscribing to topic")
client.subscribe(topic)


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


class ButtonBTEventHandler(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        # Advertisement Data
        if isNewDev:
            print "Found new device:", dev.addr, dev.getScanData()

        # Scan Response
        if isNewData:
            print "Received more data", dev.addr, dev.getScanData()

    def handleNotification(self, cHandle, data):
        # Only print the value when the handle is 40 (the battery characteristic)

        global client
        if cHandle == 40:
            receivedButton = struct.unpack('B', data)[0]

            if receivedButton == 1:
                client.publish(topic, up)
                print("Publishing message %s to topic %s" % (up, topic))
            elif receivedButton == 2:
                client.publish(topic, down)
                print("Publishing message %s to topic %s" % (down, topic))
            elif receivedButton == 3:
                client.publish(topic, right)
                print("Publishing message %s to topic %s" % (right, topic))
            elif receivedButton == 4:
                client.publish(topic, left)
                print("Publishing message %s to topic %s" % (left, topic))


button_handler = ButtonBTEventHandler()

hexiOne = Peripheral().withDelegate(button_handler)

print("Connecting to the first hexiwear")
try_until_success(hexiOne.connect, msg='error connecting to 1',
                  args=[hexiOneAddress])

print("Done connecting")
timeControl = hexiOne.getCharacteristics(uuid='2031')[0]  # Alert Input

# Get the battery service
battery = hexiOne.getCharacteristics(uuid="2a19")[0]

# Get the client configuration descriptor and write 1 to it to enable notification
battery_desc = battery.getDescriptors(forUUID=0x2902)[0]
battery_desc.write(b"\x01", True)

print("Done getting characteristics")

connectCommand = '11111111111111111111'
try_until_success(timeControl.write,
                  msg='Error sending elbow connection command', args=[connectCommand, True])

print("Hexi is good to go for pressing buttons")

while True:
    hexiOne.waitForNotifications(1.0)
