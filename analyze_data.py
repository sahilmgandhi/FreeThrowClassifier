# Turn the LED on the hexiwear on and off using bluetooth

import binascii
import struct
import bluepy.btle
from bluepy.btle import Peripheral, UUID
import time

# BT_MAC = '00:3A:40:0A:00:40'
# CMD_TURN_ON = 'ledonledonledonledon'
# CMD_TURN_OFF = 'ledoffledoffledoffle'

# hexi = Peripheral()
# hexi.connect(BT_MAC)
# ledctl = hexi.getCharacteristics(uuid='2031')[0]  # Alert Input

# for i in range(10):
#     ledctl.write(CMD_TURN_ON, True)

#     j = 0
#     while j < 1000000:
#         j = j + 1
#     ledctl.write(CMD_TURN_OFF, True)
#     j = 0
#     while j < 1000000:
#         j = j + 1


def hexStrToInt(hexstr):
    val = int(hexstr[0:2], 16) + (int(hexstr[2:4], 16) << 8)
    if ((val & 0x8000) == 0x8000):  # treat signed 16bits
        val = -((val ^ 0xffff)+1)
    return val

# hexi.disconnect()


# gyro_uuid = UUID(0x2012)
gyro_uuid = UUID(0x2002)

p = Peripheral()
p.connect('00:35:40:08:00:48')

try:
    ch = p.getCharacteristics(uuid=gyro_uuid)[0]
    print(ch)
    if (ch.supportsRead()):
        while 1:
            # print(ch.read())
            readChar = ch.read()
            print(repr(readChar))
            val = str(binascii.b2a_hex(readChar))
            print(str(val))
            print(float(hexStrToInt(val[0:4]))/100),
            print(float(hexStrToInt(val[4:8]))/100),
            print(float(hexStrToInt(val[8:12]))/100)
            time.sleep(1)

finally:
    p.disconnect()
