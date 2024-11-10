"""
Copyright 2024 William H. Beebe, Jr.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import binascii
import gc
import os
import time
import machine as ma

time.sleep_ms(250)

print()

print(f"  MACHINE: {os.uname().machine}")
print(f"  RELEASE: {os.uname().release}")
UNAME = os.uname().sysname.upper()
stat_vfs = os.statvfs('/')
fs_total = stat_vfs[0] * stat_vfs[2]
fs_free  = stat_vfs[0] * stat_vfs[3]
print(f" FS TOTAL: {fs_total:,} BYTES")
print(f" FS  FREE: {fs_free:,} BYTES")
print(f" FS  USED: {fs_total - fs_free:,} BYTES")

print(f" MEM FREE: {gc.mem_free():,} BYTES")

UNIQUE_ID = binascii.hexlify(ma.unique_id()).decode('ascii').upper()
print(f"      UID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(f"     SSID: {SSID}")
print(f" CPU FREQ: {ma.freq():,} Hz")

# Scan I2C bus for devices
#
OLED_DEVICE = None
MATX_DEVICE = None

# I2C pins for Raspberry Pi Pico 2, device I2C1
#
SDA_PIN = 4
SCL_PIN = 5
i2c = ma.SoftI2C(scl=ma.Pin(SCL_PIN), sda=ma.Pin(SDA_PIN))
print(f"      I2C: {i2c}")
i2c_scanned = i2c.scan()

if len(i2c_scanned) == 0:
    print("      I2C: No Devices Found")
else:
    print("      I2C: DEVICES FOUND:", [hex(device_address)
        for device_address in i2c_scanned])

    # Display the Micropython logo on the SSD1306 OLED display.
    #
    import SSD1306

    if SSD1306.OLED_ADDR in i2c_scanned:
        print("      I2C: FOUND OLED")
        OLED_DEVICE = SSD1306.OLED_ADDR

    if 0x70 in i2c_scanned:
        print("      I2C: FOUND FEATHERWING")
        MATX_DEVICE = 0x70

print()

WIFI = None

try:
    import network
    WIFI = network.WLAN(network.STA_IF)
except ImportError:
    print("  NETWORK: NO WIFI SUPPORT")

print()
