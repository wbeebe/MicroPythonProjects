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

from machine import Timer
import time
from ht16k33 import HT16K33Segment14

LED1_ADDR = const(0x70)
LED2_ADDR = const(0x71)
LED3_ADDR = const(0x72)
LED4_ADDR = const(0x73)

i2c = None
led1 = None
led2 = None

def clock_display_callback(timer_object):
    # Time calculation is hard-coded for EST/EDT (New York America).
    now = time.localtime(time.time() + (-4 * 3600))
    hours = now[3]
    minutes = now[4]
    seconds = now[5]

    # I can't decide if I prefer the 12 hour display or the 24 hour display,
    # so I have left (commented below) code in for both.

    # This code will produce a 24 hour clock.
    #atime = f"{hours:2d}{minutes:02d}{seconds:02d}"
    #led1.set_character(atime[0], 0).set_character(atime[1], 1).set_glyph(0x0009, 2).set_character(atime[2], 3).draw()
    #led2.set_character(atime[3], 0).set_glyph(0x0009, 1).set_character(atime[4], 2).set_character(atime[5], 3).draw()

    # This code will produce a 12 hour clock with AM/PM indicator.
    # The ':' hours and minutes separator blinks every second.
    if hours < 12:
        am_pm = 'A'
        if hours == 0:
            hours = 12
    else:
        am_pm = 'P'
        if hours > 12:
            hours -= 12
    
    # Flash the ':' separator, 1 second on, 1 second off.
    if seconds & 0x1 == 1:
        glyph = 0x0009
    else:
        glyph = 0

    atime = f"{hours:2d}{minutes:02d}"
    led1.set_character(atime[0], 0).set_character(atime[1], 1).set_glyph(glyph, 2).set_character(atime[2], 3).draw()
    led2.set_character(atime[3], 0).set_character(' ', 1).set_character(am_pm, 2).set_character('M', 3).draw()

def init(_i2c, _led1, _led2):
    global i2c, led1, led2
    i2c = _i2c
    led1 = HT16K33Segment14(i2c, i2c_address=_led1, board=HT16K33Segment14.ECBUYING_054)
    led1.set_brightness(2)
    led1.clear().draw()
    led2 = HT16K33Segment14(i2c, i2c_address=_led2, board=HT16K33Segment14.ECBUYING_054)
    led2.set_brightness(2)
    led2.clear().draw()

def start_clock():
    if i2c is None:
        return

    timer = Timer(2)
    timer.init(period=1000, mode=Timer.PERIODIC, callback=clock_display_callback)
