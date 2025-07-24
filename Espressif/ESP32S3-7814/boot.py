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
import ssd1306
import display_tools
import ht16k33_tools as htools

print( "      Boot: START")
print(f"    Memory: {gc.mem_free():,} bytes")
print(f"     Flash: {esp.flash_size():,} bytes")
PLATFORM = ' '.join(platform.platform().split('-'))
print( "  Platform: " + PLATFORM)
UNAME = os.uname().machine.split(' ')[-1]
UNIQUE_ID = binascii.hexlify(machine.unique_id()).decode('ascii').upper()
print(f" Unique ID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(f"      SSID: {SSID}")
machine.freq(160_000_000)
print(f" CPU Clock: {machine.freq():,} Hz")
#
# Scan I2C bus for devices
#
# I2C pins for ESP32-S3-DevKit1
SDA_PIN = 1
SCL_PIN = 2
SOFT_I2C = machine.SoftI2C(scl=machine.Pin(SCL_PIN), sda=machine.Pin(SDA_PIN))
print(f"       I2C: {SOFT_I2C}")

i2c_scanned = SOFT_I2C.scan()
DISPLAY = None

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

    # Check if there are HT16K33 devices attached.
    #
    if htools.LED1_ADDR in i2c_scanned and htools.LED2_ADDR in i2c_scanned:
        htools.init(SOFT_I2C, htools.LED1_ADDR, htools.LED2_ADDR)
        print("       I2C: HT16K33 LEDs Initialized")
    elif htools.LED3_ADDR in i2c_scanned and htools.LED4_ADDR in i2c_scanned:
        htools.init(SOFT_I2C, htools.LED3_ADDR, htools.LED4_ADDR)
        print("       I2C: HT16K33 LEDs Initialized")

print("      Boot: END")