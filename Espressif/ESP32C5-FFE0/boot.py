"""
    Copyright 2025 William H. Beebe, Jr.

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
import gc
import esp
import platform
import os
import binascii
import machine
from machine import Pin, SoftI2C
import ssd1306
import display_tools
import dht20

print( "      Boot: START")
print(f"    Memory: {gc.mem_free():,} bytes")
print(f"     Flash: {esp.flash_size():,} bytes")
print(f"  Platform: {' '.join(platform.platform().split('-'))}")
UNAME = os.uname().machine.split(' ')[-1]
UNIQUE_ID = binascii.hexlify(machine.unique_id()).decode('ascii').upper()
print(f" Unique ID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(f"      SSID: {SSID}")
print(f" CPU Clock: {machine.freq():,} Hz")
#
# Scan I2C bus for devices
#
# I2C pins for DFRobot ESP32-C5
SDA_PIN = 9
SCL_PIN = 10
SOFT_I2C = SoftI2C(scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
print(f"       I2C: {SOFT_I2C}")
i2c_scanned = SOFT_I2C.scan()
DISPLAY = None
DHT20 = None

if len(i2c_scanned) == 0:
    print("       I2C: No Devices Found")
else:
    print("       I2C: Devices found:", [hex(device_address)
        for device_address in i2c_scanned])

    # Check if there is an SSD1306 display attached.
    #
    if ssd1306.OLED_ADDR in i2c_scanned:
        #
        # Create instance of SSD1306 class to control the
        # display. Initialize it by clearing everything.
        #
        DISPLAY = ssd1306.SSD1306_I2C(ssd1306.OLED_WIDTH, ssd1306.OLED_HEIGHT, SOFT_I2C)
        DISPLAY.fill(0)
        print("       I2C: SSD1306 OLED Initialized")
    if dht20.FIXED_I2CADDR in i2c_scanned:
        DHT20  = dht20.DHT20(SOFT_I2C)
        print("       I2C: DHT20 Initialized")

print("      Boot: END")