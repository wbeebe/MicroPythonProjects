# This file is executed on every boot
# (including wake-boot from deepsleep)

import gc
import esp
import platform
import os
import binascii
import machine

print()
print(f"    Memory: {gc.mem_free():,} MB")
print(f"     Flash: {esp.flash_size():,} MB")
PLATFORM = ' '.join(platform.platform().split('-')[:5])
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
print( "       I2C: Devices found:", [hex(device_address)
    for device_address in SOFT_I2C.scan()])

print()