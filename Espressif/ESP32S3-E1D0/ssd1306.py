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
# MicroPython SSD1306 OLED driver, I2C interface
#
# Originally written by Adafruit
# https://github.com/adafruit/micropython-adafruit-ssd1306/
#
# Adafruit has deprecated this code, and is now devoting
# development time and resources for the version that
# works with Circuit Python.

import time
import framebuf
import devices
from machine import Pin, SoftI2C

# register definitions
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xa4)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xa0)
SET_MUX_RATIO       = const(0xa8)
SET_COM_OUT_DIR     = const(0xc0)
SET_DISP_OFFSET     = const(0xd3)
SET_COM_PIN_CFG     = const(0xda)
SET_DISP_CLK_DIV    = const(0xd5)
SET_PRECHARGE       = const(0xd9)
SET_VCOM_DESEL      = const(0xdb)
SET_CHARGE_PUMP     = const(0x8d)

# Default display definitions
#OLED_WIDTH    = const(128)
#OLED_HEIGHT   = const(64)
#OLED_HEIGHT   = const(64)
#OLED_ADDR     = const(0x3D)

class SSD1306:
    def __init__(self, width, height, scl_pin, sda_pin, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.i2c = None
        self.device_active = False
        try:
            self.i2c = SoftI2C(scl=scl_pin, sda=sda_pin, freq=250000)
            i2c_scanned = self.i2c.scan()
            if len(self.i2c_scanned) > 0 and OLED_ADDR in i2c_scanned:
                self.device_active = True
        except:
            pass

        self.poweron()
        self.init_display()

    def init_display(self):
        if not self.device_active:
            return

        for cmd in (
            SET_DISP | 0x00, # off
            # address setting
            SET_MEM_ADDR, 0x00, # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL, 0x30, # 0.83*Vcc
            # display
            SET_CONTRAST, 0xff, # maximum
            SET_ENTIRE_ON, # output follows RAM contents
            SET_NORM_INV, # not inverted
            # charge pump
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01): # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        if self.device_active:
            self.write_cmd(SET_DISP | 0x00)

    def contrast(self, contrast):
        if self.device_active:
            self.write_cmd(SET_CONTRAST)
            self.write_cmd(contrast)

    def invert(self, invert):
        if self.device_active:
            self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        if self.device_active:
            return

        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_framebuf()

    def fill(self, col):
        if self.device_active:
            self.framebuf.fill(col)

    def pixel(self, x, y, col):
        if self.device_active:
            self.framebuf.pixel(x, y, col)

    def scroll(self, dx, dy):
        if self.device_active:
            self.framebuf.scroll(dx, dy)

    def text(self, string, x, y, col=1):
        if self.device_active:
            self.framebuf.text(string, x, y, col)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, scl_pin, sda_pin, addr=0x3c, external_vcc=False):
        self.addr = addr
        self.temp = bytearray(2)
        # Add an extra byte to the data buffer to hold an I2C data/command byte
        # to use hardware-compatible I2C transactions.  A memoryview of the
        # buffer is used to mask this byte from the framebuffer operations
        # (without a major memory hit as memoryview doesn't copy to a separate
        # buffer).
        self.buffer = bytearray(((height // 8) * width) + 1)
        self.buffer[0] = 0x40  # Set first byte of data buffer to Co=0, D/C=1
        self.framebuf = framebuf.FrameBuffer1(memoryview(self.buffer)[1:], width, height)
        super().__init__(width, height, scl_pin, sda_pin, external_vcc)

    def write_cmd(self, cmd):
        if self.device_active:
            self.temp[0] = 0x80 # Co=1, D/C#=0
            self.temp[1] = cmd
            self.i2c.writeto(self.addr, self.temp)

    def write_framebuf(self):
        # Blast out the frame buffer using a single I2C transaction to support
        # hardware I2C interfaces.
        if self.device_active:
            self.i2c.writeto(self.addr, self.buffer)

    def poweron(self):
        pass

    # A convenience method to print by line number unlike the text() method.
    # This assumes that you are using a 128 x 64 pixel OLED display.
    # Line numbers are 1-6 inclusive. There is no line 0.
    #
    def line(self, string, line_number):
        if self.device_active:
            if line_number > 0 and line_number <= devices.OLED_LINE_MAX:
                self.text(string,0,(line_number - 1)*10)

    # A convenience method to print one, and only one line on a display.
    # The entire display is erased before the single line is then displayed.
    #
    def show_only_one_line(self, msg):
        if self.device_active:
            self.fill(0)
            self.line(msg,1)
            self.show()

    # A way to test a 128 x 64 pixel OLED display.
    #
    def test_oled(self):
        if not self.device_active:
            return

        for i in range(1, devices.OLED_LINE_MAX + 1):
            self.fill(0)
            self.line(f'LINE {i} ----+----', i)
            self.show()
            time.sleep_ms(500)

        self.fill(0)
        self.show()
