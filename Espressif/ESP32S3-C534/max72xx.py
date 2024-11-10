"""
MAX7219/MAX7221 cascadable 8x8 LED matrix management class.

Copyright 2024 William H. Beebe, Jr

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

from micropython import const
#
# Command registers. Destinations to send commands and data to.
#
ROW_0        = const(0x01)
DECODE_MODE  = const(0x09)
INTENSITY    = const(0x0A)
SCAN_LIMIT   = const(0x0B)
SHUTDOWN     = const(0x0C)
DISPLAY_TEST = const(0x0F)

ENABLE  = const(0)
DISABLE = const(1)

"""
Controller class for cascading MAX72xx 8x8 LED matrices.

# Example code for MicroPython 1.22 running on an
# ESP32-S3-DevKitC-1.1-N8R8

from machine import Pin, SPI
import max72xx

spi = SPI(1, 10000000, sck=Pin(12), mosi=Pin(11))
chip_select = Pin(10, Pin.OUT)
character_display_count = 8

display = max72xx.Matrix8x8(spi, chip_select, character_display_count)
display.text('1234!@#$',0,0)
display.show()
"""
import framebuf

class MAX72XX(framebuf.FrameBuffer):
    def __init__(self, spi_device, chip_select, number_of_digits):
        self.spi_device = spi_device
        self.chip_select = chip_select
        self.chip_select.init(chip_select.OUT, True)
        self.buffer = bytearray(number_of_digits * 8)
        self.number_of_digits = number_of_digits
        super().__init__(self.buffer, 8 * number_of_digits, 8, framebuf.MONO_HLSB)
        self.init()

    def init(self):
        self.write_command_data(SHUTDOWN,     0)
        self.write_command_data(DISPLAY_TEST, 0)
        self.write_command_data(SCAN_LIMIT,   7)
        self.write_command_data(DECODE_MODE,  0)
        self.write_command_data(SHUTDOWN,     1)

    def write_command_data(self, command, data):
        self.chip_select(ENABLE)
        for _ in range(self.number_of_digits):
            self.spi_device.write(bytearray([command, data]))
        self.chip_select(DISABLE)
    
    def show(self):
        for y in range(8):
            self.chip_select(ENABLE)
            for digit in range(self.number_of_digits):
                self.spi_device.write(
                    bytearray([ROW_0 + y, self.buffer[(y * self.number_of_digits) + digit]]))
            self.chip_select(DISABLE)

    # Fills the display with binary zeroes, turning off every LED and
    # thus blanking the display.
    # Once cleared you must reload the display controller buffers with data
    # again via text() then call show().
    #
    def clear(self):
        self.chip_select(ENABLE)
        self.fill(0)
        self.show()
        self.chip_select(DISABLE)

    # LED display intensity can range from 0 to 15 inclusive
    #
    def intensity(self, value):
        self.chip_select(ENABLE)
        self.write_command_data(INTENSITY, (value & 0x0F))
        self.chip_select(DISABLE)

    # Convenience function. Scrolls the buffer down one pixel line,
    # filling the top line with binary zeroes to turn off any lingering
    # lit pixels.
    #
    def scroll_down_one_line(self):
        self.scroll(0, 1)
        self.hline(0, 0, (self.number_of_digits * 8), 0)
        self.show()

    # Convenience function. Scrolls the buffer up one pixel line,
    # filling the bottom line with binary zeroes to turn off any lingering
    # lit pixels.
    #
    def scroll_up_one_line(self):
        self.scroll(0, -1)
        self.hline(0, 7, (self.number_of_digits * 8), 0)
        self.show()

    # Convenience function. Scrolls the buffer to the right one pixel column,
    # filling the far left column with binary zeroes to turn off any lit pixels.
    #
    def scroll_right_one_line(self):
        self.scroll(1, 0)
        self.vline(0, 0, 8, 0)
        self.show()

    # Convenience function. Scrolls the buffer to the left one pixel column,
    # filling the far right column with binary zeroes to turn off any lit pixels.
    #
    def scroll_left_one_line(self):
        self.scroll(-1, 0)
        self.vline((self.number_of_digits * 8) - 1, 0, 8, 0)
        self.show()
