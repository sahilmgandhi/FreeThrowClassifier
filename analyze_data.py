# Turn the LED on the hexiwear on and off using bluetooth

import bluepy.btle
from bluepy.btle import Peripheral
import time

BT_MAC = '00:3A:40:0A:00:40'
CMD_TURN_ON = 'ledonledonledonledon'
CMD_TURN_OFF = 'ledoffledoffledoffle'

hexi = Peripheral()
hexi.connect(BT_MAC)
ledctl = hexi.getCharacteristics(uuid='2031')[0]  # Alert Input

for i in range(10):
    ledctl.write(CMD_TURN_ON, True)

    j = 0
    while j < 1000000:
        j = j + 1
    ledctl.write(CMD_TURN_OFF, True)
    j = 0
    while j < 1000000:
        j = j + 1


hexi.disconnect()
