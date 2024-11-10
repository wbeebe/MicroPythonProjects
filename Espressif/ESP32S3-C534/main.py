"""
MAX7219/MAX7221 cascadable 8x8 LED matrix example application.
Parallax SIM33EAU GPS Module example application.
Concurrent/asyncio example application.

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
import gc
print(f"  MEM: {gc.mem_free():,} MB")

import esp
print(f"FLASH: {esp.flash_size():,} MB")

import platform
print(f" PLAT: {platform.platform()}")

import os
UNAME = os.uname()[-1].split(' ')[-1]

import binascii
import machine
UNIQUE_ID = binascii.hexlify(machine.unique_id()).decode('ascii').upper()
print(f"  UID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
SSID_S = UNAME[0] + UNAME[-2:] + '-' + UNIQUE_ID[-4:]
print(f" SSID: {SSID}")
#
# Driving eight character, 8x8 LED, MAX72XX device purchased from
# Amazon: https://www.amazon.com/dp/B0BXDNCVRT
#
import asyncio
from machine import Pin, SPI
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
display.show()

import time
print(" WAITING 10 SECONDS")
time.sleep_ms(10_000)
print(" RESUMING EXECUTION\n")
#
# Test scrolling.
# Scroll up, then down, then left, then right.
#
async def test_scrolling():
    print(" Start test_scrolling")
    scroll_direction = 0
    string_length = len(SSID_S)
    range_count = string_length
    delay_in_ms = 50

    while True:
        for _ in range(4):
            display.text(SSID_S, 0, 0)
            display.show()
            await asyncio.sleep_ms(2_000)

            for _ in range(range_count):
                if scroll_direction == 0:
                    display.scroll_up_one_line()
                elif scroll_direction == 1:
                    display.scroll_down_one_line()
                elif scroll_direction == 2:
                    display.scroll_left_one_line()
                elif scroll_direction == 3:
                    display.scroll_right_one_line()
                await asyncio.sleep_ms(delay_in_ms)

            scroll_direction = (scroll_direction + 1) & 0x03
            range_count = string_length + ((scroll_direction & 2) * (string_length - 1) * 8)
            delay_in_ms = 50 - (scroll_direction & 2) * 20
            await asyncio.sleep_ms(2_000)
#
# GPS module read.
# Using a hacked version of Adafruit's CircuitPython GPS module
# ported back to MicroPython.
# Module: https://github.com/pepijndevos/Adafruit_MicroPython_GPS
#
# Create UART instance to talk to Parallax SIM33EAU Rev C GPS module.
# Component: https://www.parallax.com/product/sim33eau-gps-module/
#
from machine import UART
uart = UART(2, baudrate=9600, rx=18)

import gps_parser
gps = gps_parser.GPS(uart)

month_names = [
    "Jan", "Feb", "March",
    "April", "May", "June",
    "July", "August", "Sept",
    "Oct", "Nov", "Dec"]

async def read_uart():
    print(" Start read_uart")
    print_count = 0

    while True:
        gps.update()
        
        if gps.has_fix:
            print(f"GPS {gps.latitude:.6f}, {gps.longitude:.6f}", end="")
            gt = gps.timestamp_utc
            print_count += 1

            if gt[0] != 0:
                month_name = month_names[gt[1] - 1]
                print(f", {gt[2]} {month_name} {gt[0]} - {gt[3]:02}:{gt[4]:02} GMT, #{print_count}")
            else:
                print(f", #{print_count}")
        else:
            print(" no GPS fix")

        await asyncio.sleep_ms(10_000)
#
# Spawn the concurrent tasks here.
#
async def main():
    asyncio.create_task(test_scrolling())
    asyncio.create_task(read_uart())
    while True:
        await asyncio.sleep_ms(100)
#
# Kick everything off.
#
asyncio.run(main())
