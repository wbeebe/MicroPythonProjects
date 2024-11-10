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
import SSD1306

# Display the Micropython logo on the SSD1306 OLED display.
#
def display_micropython_logo(display):
    display.framebuf.fill_rect(0, 0, 32, 32, 1)
    display.framebuf.fill_rect(2, 2, 28, 28, 0)
    display.framebuf.vline(9, 8, 22, 1)
    display.framebuf.vline(16, 2, 22, 1)
    display.framebuf.vline(23, 8, 22, 1)
    display.framebuf.fill_rect(26, 24, 2, 4, 1)
    return display

# Create a graphic of the Raspberry Pi logo.
# Display it twice, one logo for each active Pico/Pico 2 core,
# similar to what the regular Raspberry Pi does on initial boot.
# I copied the bytearray for the logo from Raspberry Pi itself:
# https://github.com/raspberrypi/pico-micropython-examples/tree/master/i2c
#
# I split up the single long line into a series of shorter concatenations
# for better readability.
#
def create_rpi_logo():
    buffer = bytearray(
              b"\x00\x00\x00\x00\x00\x00\x00\x00")
    buffer += b"\x00\x00\x00\x00\x00\x7C\x3F\x00"
    buffer += b"\x01\x86\x40\x80\x01\x01\x80\x80"
    buffer += b"\x01\x11\x88\x80\x01\x05\xa0\x80"
    buffer += b"\x00\x83\xc1\x00\x00C\xe3\x00\x00"
    buffer += b"\x7e\xfc\x00\x00\x4c\x27\x00\x00"
    buffer += b"\x9c\x11\x00\x00\xbf\xfd\x00\x00"
    buffer += b"\xe1\x87\x00\x01\xc1\x83\x80\x02A"
    buffer += b"\x82@\x02A\x82@\x02\xc1\xc2@\x02"
    buffer += b"\xf6>\xc0\x01\xfc=\x80\x01\x18\x18"
    buffer += b"\x80\x01\x88\x10\x80\x00\x8c!\x00"
    buffer += b"\x00\x87\xf1\x00\x00\x7f\xf6\x00"
    buffer += b"\x008\x1c\x00\x00\x0c\x20\x00\x00"
    buffer += b"\x03\xc0\x00\x00\x00\x00\x00\x00"
    buffer += b"\x00\x00\x00\x00\x00\x00\x00"
    return buffer
