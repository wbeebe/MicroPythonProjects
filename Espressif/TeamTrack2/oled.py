"""
Class to support displaying information to an external character display.
These displays are attached to the Pycom devices, specifically
Pytrack V2, through the Pytracks I2C PyPort 1.
"""
from machine import I2C
from machine import Pin
from micropython import const
import framebuf

import config


# register definitions
SET_CONTRAST    = const(0x81)
SET_ENTIRE_ON   = const(0xA4)
SET_NORM_INV    = const(0xA6)
SET_DISP        = const(0xAE)
SET_MEM_ADDR    = const(0x20)
SET_COL_ADDR    = const(0x21)
SET_PAGE_ADDR   = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP   = const(0xA0)
SET_MUX_RATIO   = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE   = const(0xD9)
SET_VCOM_DESEL  = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
#
class OledTTrk(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)

        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,            # off
            SET_MEM_ADDR,               # address setting
            0x00,                       # horizontal
            SET_DISP_START_LINE | 0x00, # resolution and layout
            SET_SEG_REMAP | 0x01,       # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,     # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            SET_DISP_CLK_DIV,           # timing and driving scheme
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,                       # 0.83*Vcc
            SET_CONTRAST,               # display
            0xFF,                       # maximum
            SET_ENTIRE_ON,              # output follows RAM contents
            SET_NORM_INV,               # not inverted
            SET_CHARGE_PUMP,            # charge pump
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)

        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
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
        self.write_data(self.buffer)


class Oled_I2C(OledTTrk):
    def __init__(self, width, height, i2c, addr, external_vcc=False):

        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writeto(self.addr, b'\x40'+buf)
