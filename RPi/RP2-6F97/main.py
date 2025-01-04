import gc
import os
import platform
import binascii
import machine as ma
import time
import SSD1306
import display_tools
import webpage
import ntptime

print(f"\n MEM FREE: {gc.mem_free():,} BYTES")
UNAME = os.uname().sysname.upper()
stat_vfs = os.statvfs('/')
fs_total = stat_vfs[0] * stat_vfs[2]
fs_free  = stat_vfs[0] * stat_vfs[3]
fs_used  = fs_total - fs_free
print(f" FS TOTAL: {fs_total:,} BYTES")
print(f" FS  FREE: {fs_free:,} BYTES")
print(f" FS  USED: {fs_used:,} BYTES")
print(f" PLATFORM: {platform.platform()}")

UNIQUE_ID = binascii.hexlify(ma.unique_id()).decode('ascii').upper()
print(f"      UID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(f"     SSID: {SSID}")
print(f" CPU FREQ: {ma.freq():,} Hz")
#
# Scan I2C bus for devices
#
SDA_PIN = ma.Pin(4) # Blue wire
SCL_PIN = ma.Pin(5) # Yellow wire
#I2C = ma.I2C(0, scl=SCL_PIN, sda=SDA_PIN, freq=250000)
I2C = ma.SoftI2C(scl=SCL_PIN, sda=SDA_PIN, freq=250000)
print(f"      I2C: {I2C}")
i2c_scanned = I2C.scan()

if len(i2c_scanned) == 0:
    print("      I2C: No Devices Found")
else:
    print("      I2C: DEVICES FOUND:", [hex(device_address)
        for device_address in i2c_scanned])

    # Check if there is an SSD1306 display attached.
    #
    if SSD1306.OLED_ADDR in i2c_scanned:
        print("      I2C: SSD1306 OLED")
        #
        # Create instance of SSD1306 class to control the
        # display. Initialize it by clearing everything.
        #
        display = SSD1306.SSD1306_I2C(I2C)
        display.fill(0)
        display_tools.do_graphics(display, platform.platform(), SSID)

#
# Set up to use on-board LED
#
led = ma.Pin("LED", ma.Pin.OUT)
led.value(0)

import network
import socket
import settings

wifi = network.WLAN(network.STA_IF)
network.hostname(SSID)
wifi.active(True)
wifi.connect(settings.AP_SSID, settings.AP_PWRD)

while wifi.isconnected() == False:
    time.sleep_ms(1000)

attempts = 10
while attempts > 0:
    try:
        ntptime.settime()
        attempts = 0
    except Exception as te:
        print(te)
        time.sleep_ms(1000)
        attempts -= 1

ip = wifi.ifconfig()[0]
print(f"     WIFI: {ip}")
display.text(str(ip), 0, 36, 1)
display.show()

address = (ip, 80)
connection = socket.socket()
connection.bind(address)
connection.listen(4)

print(f"     WIFI: Ready {ip}")

while True:
    client = connection.accept()[0]
    request = str(client.recv(2048))
    #print(request)
    if 'LED+OFF=OFF' in request:
        led.value(0)
    if 'LED+ON=ON' in request:
        led.value(1)
    if 'DISPLAY+ON=ON' in request:
        display_tools.do_graphics(display, platform.platform(), SSID)
        display.text(str(ip), 0, 36, 1)
        display.show()
    if 'DISPLAY+OFF=OFF' in request:
        display.fill(0)
        display.show()

    client.send(webpage.webpage(SSID))
    client.close()
