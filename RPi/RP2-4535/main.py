import gc
import os
import platform
import machine as ma
import binascii
import time
import SSD1306
import display_tools

print(f"\n MEM FREE: {gc.mem_free():,} BYTES")
UNAME = os.uname().sysname.upper()
stat_vfs = os.statvfs('/')
fs_total = stat_vfs[0] * stat_vfs[2]
fs_free  = stat_vfs[0] * stat_vfs[3]
fs_used  = fs_total - fs_free
print(f" FS TOTAL: {fs_total:,} BYTES")
print(f" FS  FREE: {fs_free:,} BYTES")
print(f" FS  USED: {fs_used:,} BYTES")
print(f" PLATFORM: {platform.platform().replace('--', ' ').replace('-', ' ')}")
print(f" CPU FREQ: {ma.freq():,} Hz")
UNIQUE_ID = binascii.hexlify(ma.unique_id()).decode('ascii').upper()
print(f"      UID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(f"     SSID: {SSID}")
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

import webserver
webserver.run(SSID, display, led)