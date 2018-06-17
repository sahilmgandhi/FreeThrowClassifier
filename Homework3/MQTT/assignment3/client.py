
import paho.mqtt.client as mqtt
import time

macFile = open("mac.txt", "r")
hexiOneAddress = str(macFile.readline().rstrip())
print(hexiOneAddress)
macFile.close()


# broker to connect to
broker = "broker.hivemq.com"

topic = "ecem119/2018s/hexiwear/" + hexiOneAddress

# callback function for connection


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Broker connection successful")
    else:
        print("Error connecting to broker")

# callback for messages


def on_message(client, userdata, message):
    print("%s @ %s" % (str(message.payload.decode("utf-8")), hexiOneAddress))


print("Creating new instance")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker: %s" % broker)
client.connect(broker)
client.loop_start()

print("Subscribing to topic: %s" % topic)
client.subscribe(topic)

client.loop_forever()
