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
import config
import display_tools as dt
import framebuf
from machine import Pin, Timer
import time

print(config.version_name)
print(config.compiler)
print(config.build_date)

board_led = Pin("LED", Pin.OUT)
board_led.value(0)

import rp2
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def blink():
    wrap_target()
    set(pins, 1)   [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    set(pins, 0)   [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    nop()          [31]
    wrap()

sm = rp2.StateMachine(0, blink, freq=2400, set_base=Pin(22))
sm.active(1)

from gpio_lcd import GpioLcd
lcd = GpioLcd(rs_pin=Pin(16),
              enable_pin=Pin(17),
              d4_pin=Pin(18),
              d5_pin=Pin(19),
              d6_pin=Pin(20),
              d7_pin=Pin(21),
              num_lines=4, num_columns=20)
lcd.clear()
lcd.putstr(os.uname().machine.split(' ')[2] + " @ " + SSID)
lcd.move_to(0,1)
lcd.putstr(os.uname().machine.split(' ')[-1])
lcd.move_to(0,2)
lcd.putstr("Version " + config.version_name)
lcd.move_to(0,3)
lcd.putstr("Compiled " + config.build_date)

display = None

if OLED_DEVICE is not None:
    display = SSD1306.SSD1306_I2C(i2c)
    display.fill(0)
    dt.display_micropython_logo(display)
    _machine = os.uname().machine.split(' ')[-1]
    if "RISCV" in _machine:
        _machine = _machine.replace("RISCV", "RV")
    display.text(_machine, 36, 0, 1)
    display.text(os.uname().release.split('-')[0], 36, 12, 1)
    display.text(SSID, 36, 24, 1)

    logo = dt.create_rpi_logo()
    raspberry_pi_logo = framebuf.FrameBuffer(logo, 32, 32, framebuf.MONO_HLSB)
    display.framebuf.blit(raspberry_pi_logo, 0, 34)
    display.framebuf.blit(raspberry_pi_logo, 30, 34)

    display.show()

matrix = None

if MATX_DEVICE is not None:
    # If we have an Adafruit Matrix Featherwing attached then display
    # text and an icon on it.
    #
    from ht16k33 import ht16k33matrixfeatherwing as matx
    matrix = matx.HT16K33MatrixFeatherWing(i2c)
    matrix.set_brightness(2)
    matrix.clear().draw()

    text = "        0123456789 abcdefghijklmnopqrstuvwxyz !$%&*() \x00\x01        "
    matrix.scroll_text(text)

    # Finish by drawing a smiley face.
    icon = b"\x3C\x42\xA9\x85\x85\xA9\x42\x3C"
    matrix.clear().set_icon(icon, 4).draw()

if WIFI is not None:
    WIFI.active(True)
    access_points = WIFI.scan()
    networks = {}

    for network in access_points:
        if len(network[0]) > 0 and bytearray(network[0])[0] != 0:
            ssid = network[0].decode('utf-8')
            networks[ssid] = network[3]

    for ssid in sorted(networks.keys()):
        print(f"ssid: {ssid:24} rssi: {networks[ssid]}")

def one_shot_callback(t):
    lcd.clear()
    sm.active(0)
    sm.exec("set(pins, 0)")

    if display is not None:
        display.fill(0)
        display.show()

    if matrix is not None:
        matrix.clear().draw()

one_shot = Timer()
one_shot.init(period=120000, mode=Timer.ONE_SHOT, callback=one_shot_callback)

def led_timer_callback(t):
    board_led.toggle()

led_timer = Timer()
led_timer.init(freq=1, mode=Timer.PERIODIC, callback=led_timer_callback)
