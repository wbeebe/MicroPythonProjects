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
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import gc
import esp
import platform
import os
import binascii
import machine

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
print(f" CPU Clock: {machine.freq():,} Hz")
print("      Boot: END")
