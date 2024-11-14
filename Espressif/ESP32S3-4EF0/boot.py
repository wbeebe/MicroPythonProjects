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
# This file is executed on every boot
# (including wake-boot from deepsleep)
# This provides global board info in variables
# used by other scripts.

print()

import gc
MEM_FREE = gc.mem_free()
print("  MEM: {:,} MB".format(MEM_FREE))

import esp
FLASH_SIZE = esp.flash_size()
print("FLASH: {:,} MB".format(FLASH_SIZE))

import platform
PLATFORM = platform.platform()
print(" PLAT: {}".format(PLATFORM))

import os
UNAME = os.uname()[-1].split(' ')[0]

import binascii
import machine
UNIQUE_ID = binascii.hexlify(machine.unique_id()).decode('ascii').upper()
print("  UID: {}".format(UNIQUE_ID))
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(" SSID: {}".format(SSID))

import machine
from micropython import const
# The frequency must be 20MHz, 40MHz, 80Mhz, 160MHz or 240MHz
# 
machine.freq(240_000_000)
print(" FREQ: {:,} Hz".format(machine.freq()))

# Scan I2C bus for devices
#
# I2C pins for ESP32-S3-DevKit1
from config import SCL_PIN, SDA_PIN
from machine import Pin
SOFT_I2C = machine.SoftI2C(scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
print("  I2C: {}".format(SOFT_I2C))
print("  I2C: Addresses found:", [hex(device_address)
    for device_address in SOFT_I2C.scan()])

print()

# Testing phototransistor and ADC input
#
#from machine import Pin, ADC
#from time import sleep
#alog = ADC(Pin(4))
#alog.atten(ADC.ATTN_11DB)
#count = 30
#for x in range(count):
#    _value = alog.read()
#    print("{:>2} {}".format(x,_value))
#    sleep(2)