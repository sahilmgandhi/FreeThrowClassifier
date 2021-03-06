# Using Hexiwear with Python
import pexpect
import time

DEVICE = "00:35:40:08:00:48"

print("Hexiwear address:"),
print(DEVICE)

# Run gatttool interactively.
print("Run gatttool...")
child = pexpect.spawn("gatttool -I")


# Connect to the device.
print("Connecting to "),
print(DEVICE)
con = "connect 00:35:40:08:00:48"
child.sendline(con)
child.expect("Connection successful", timeout=5)
print(" Connected!")

# function to transform hex string like "0a cd" into signed integer


def hexStrToInt(hexstr):
    val = int(hexstr[0:2], 16) + (int(hexstr[3:5], 16) << 8)
    if ((val & 0x8000) == 0x8000):  # treat signed 16bits
        val = -((val ^ 0xffff)+1)
    return val


# while True:
# Accelerometer
child.sendline("char-read-uuid 0x2001")
child.expect("handle: ", timeout=10)
child.expect("\r\n", timeout=10)
trimmedString = child.before[child.before.find(":")+2:]
print("Accel: "),
print(trimmedString),
print(float(hexStrToInt(trimmedString[0:5]))/100),
print(float(hexStrToInt(trimmedString[6:11]))/100),
print(float(hexStrToInt(trimmedString[12:17]))/100)

# Gyroscope
child.sendline("char-read-uuid 0x2002")
child.expect("handle: ", timeout=10)
child.expect("\r\n", timeout=10)
trimmedString = child.before[child.before.find(":")+2:]
print("Gyro: "),
print(trimmedString),
print(float(hexStrToInt(trimmedString[0:5]))/100),
print(float(hexStrToInt(trimmedString[6:11]))/100),
print(float(hexStrToInt(trimmedString[12:17]))/100)

# Magnetometer
child.sendline("char-read-uuid 0x2003")
child.expect("handle: ", timeout=10)
child.expect("\r\n", timeout=10)
trimmedString = child.before[child.before.find(":")+2:]
print("Magneto:"),
print(trimmedString),
print(hexStrToInt(trimmedString[0:5])),
print(hexStrToInt(trimmedString[6:11])),
print(hexStrToInt(trimmedString[12:17]))

# while True:
# Accelerometer
child.sendline("char-read-hnd 0x30")
child.expect("Characteristic value/descriptor: ", timeout=10)
child.expect("\r\n", timeout=10)
print("Accel: "),
print(child.before),
print(float(hexStrToInt(child.before[0:5])) / 100),
print(float(hexStrToInt(child.before[6:11])) / 100),
print(float(hexStrToInt(child.before[12:17]))/100)

# Gyroscope
child.sendline("char-read-hnd 0x34")
child.expect("Characteristic value/descriptor: ", timeout=10)
child.expect("\r\n", timeout=10)
print("Gyro: "),
print(child.before),
print(float(hexStrToInt(child.before[0:5])) / 100),
print(float(hexStrToInt(child.before[6:11])) / 100),
print(float(hexStrToInt(child.before[12:17]))/100)

# Magnetometer
child.sendline("char-read-hnd 0x38")
child.expect("Characteristic value/descriptor: ", timeout=10)
child.expect("\r\n", timeout=10)
print("Magneto:"),
print(child.before),
print(hexStrToInt(child.before[0:5])),
print(hexStrToInt(child.before[6:11])),
print(hexStrToInt(child.before[12:17]))
