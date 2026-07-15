"""
MAX7219/MAX7221 cascadable 8x8 LED matrix example application.
HT16K33/VT16K33 14-segment LED display example application.
Parallax SIM33EAU GPS Module example application.
Concurrent/asyncio example application.

Copyright 2026 William H. Beebe, Jr.

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
print(f"     MEMORY: {gc.mem_free():,} MB")

import esp
print(f" FLASH SIZE: {esp.flash_size():,} MB")

import platform
print("   PLATFORM: " + platform.platform().replace("-"," "))

import os
UNAME = os.uname()[-1].split(' ')[-1]

import machine
UNIQUE_ID = ''.join("{:02X}".format(byte) for byte in machine.unique_id())

print(f"        UID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
SSID_S = UNAME[0] + UNAME[-2:] + '-' + UNIQUE_ID[-4:]
print(f"       SSID: {SSID}")
print(f"     SSID_S: {SSID_S}\n")
#
# For HT16K33/VT16K33 14-segment LED displays
#
from machine import SoftI2C, Pin
from ht16k33 import HT16K33Segment14
i2c = SoftI2C(scl=Pin(2), sda=Pin(1))
print(i2c.scan())
led = HT16K33Segment14(i2c, board=HT16K33Segment14.SPARKFUN_ALPHA)
led.set_brightness(2)
led.clear().draw()
led.set_character("T", 0).set_character("E", 1)
led.set_character("S", 2).set_character("T", 3).draw()
#
# Driving 8 character, 8x8 LED array, driven by a MAX72XX device.
#
import asyncio
from machine import SPI
import max72xx
#
# Initialize the SPI bus to communicate with a MAX72XX device,
# then clear the MAX72XX display by turning off all LEDs.
#
spi = SPI(1, 10000000, sck=Pin(12), mosi=Pin(11))
chip_select = Pin(10, Pin.OUT)
display=max72xx.MAX72XX(spi, chip_select, 8)
display.fill(0)
display.intensity(0)
# Display the version of MicroPython we're running with for 10 seconds.
display.text(f"*{platform.platform().split('-')[1]}*", 0, 0)
display.show()

import time
print(" WAITING 10 SECONDS")
time.sleep_ms(10_000)
print(" RESUMING EXECUTION\n")
display.fill(0)
#
# Text scrolling with an 8 character, 8x8 LED array, display.
# EC Buying MAX7219 Dot Matrix 8 in 1 Display Module for Arduino Microcontroller
# Purchased from Amazon: https://www.amazon.com/dp/B0BXDNCVRT
#
# Scroll up, then down, then left, then right.
#
async def scroll_text():
    print(f" Start scrolling \"{SSID_S}\"")

    while True:
        for scroll_direction in range(4):

            if scroll_direction == 0:
                range_count = 8
                scroll_function = display.scroll_up_one_line
            elif scroll_direction == 1:
                range_count = 8
                scroll_function = display.scroll_down_one_line
            elif scroll_direction == 2:
                range_count = 64
                scroll_function = display.scroll_left_one_line
            else:
                range_count = 64
                scroll_function = display.scroll_right_one_line

            display.text(SSID_S, 0, 0)
            display.show()
            await asyncio.sleep_ms(2_000)

            for _ in range(range_count):
                scroll_function()

            await asyncio.sleep_ms(1_000)
#
# Read the GPS hardware.
# Using a hacked version of Adafruit's CircuitPython GPS module
# ported back to MicroPython.
# Module: https://github.com/pepijndevos/Adafruit_MicroPython_GPS
#
# Create UART instance to talk to Parallax SIM33EAU Rev C GPS module.
# Component: https://www.parallax.com/product/sim33eau-gps-module/
#
from machine import Pin, UART
fix_status = Pin(17, Pin.IN, Pin.PULL_DOWN)
uart = UART(2, baudrate=9600, rx=18)

import gps_parser
gps = gps_parser.GPS(uart)

async def read_gps():
    print(" Start reading GPS")
    only_show_gps = True
    print_count = 0
    month_names = [
        "January", "February","March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"]

    while True:
        await asyncio.sleep_ms(30_000)
        
        # Testing status of SIM33EAU FIX pen. Active high means the module has
        # gotten its GPS fix. If it's low, meaning no fix, then just bypass
        # everything.
        if fix_status == 0:
            continue

        gps.update()
        
        if gps.has_fix:
            print_count += 1
            text_count = "{:04}".format(print_count)
            led.clear().draw()
            led.set_character(text_count[0], 0).set_character(text_count[1], 1)
            led.set_character(text_count[2], 2).set_character(text_count[3], 3).draw()
            
            print(f"GPS {gps.latitude:.6f}, {gps.longitude:.6f}", end="")

            if only_show_gps:
                print(f", #{print_count}")
            else:
                gt = gps.timestamp_utc

                if gt[0] != 0:
                    month_name = month_names[gt[1] - 1]
                    print(f", {gt[2]} {month_name} {gt[0]} - {gt[3]:02}:{gt[4]:02} GMT, #{print_count}")
                else:
                    print(f", #{print_count}")
        else:
            print(" No GPS Fix")
            led.clear().draw()
            led.set_character("*", 0).set_character("*", 1)
            led.set_character("*", 2).set_character("*", 3).draw()

#
# Create concurrent tasks here.
#
async def main():
    asyncio.create_task(scroll_text())
    asyncio.create_task(read_gps())
    while True:
        await asyncio.sleep_ms(100)
#
# Start everything.
#
asyncio.run(main())
