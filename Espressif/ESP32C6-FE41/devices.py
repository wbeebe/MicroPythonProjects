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

from micropython import const
import machine as ma
import neopixel as neo
import time as ti

LED_RED = (32, 0, 0)
LED_GREEN = (0, 32, 0)
LED_BLUE = (0, 0, 32)
LED_CYAN = (0, 32, 32)
LED_MAGENTA = (32, 0, 32)
LED_YELLOW = (32, 16, 0)
LED_OFF = (0, 0, 0)

neopixel_colors = [
    LED_RED,
    LED_GREEN,
    LED_BLUE,
    LED_CYAN,
    LED_MAGENTA,
    LED_YELLOW,
    LED_OFF
    ]

# ESP32-S3-DevKitC-1 v1.0 NeoPixel pin
#pinnum = const(48)
# ESP32-S3-DevKitC-1 v1.1 NeoPixel pin
#pinnum = const(38)
# ESP32-C6-DevKitC-1 v1.2 NeoPixel pin
pinnum = const(8)
np = neo.NeoPixel(ma.Pin(pinnum), 1)

_last_led_color = LED_OFF

def cycle_colors():
    global _last_led_color
    for color in neopixel_colors:
        np[0] = color
        np.write()
        ti.sleep_ms(400)
        
    _last_led_color = LED_OFF

def set_led_color(color):
    global _last_led_color
    np[0] = color
    _last_led_color = color
    np.write()

def toggle_led_color(new_color):
    global _last_led_color
    state = "OFF"

    if new_color is _last_led_color:
        set_led_color(LED_OFF)
    else:
        set_led_color(new_color)
        state = "ON"

    return state

def blink_neopixel():
    global _last_led_color
    np[0] = LED_OFF
    np.write()
    ti.sleep_ms(100)
    np[0] = LED_RED
    np.write()
    ti.sleep_ms(100)
    np[0] = LED_OFF
    np.write()
    ti.sleep_ms(100)
    np[0] = _last_led_color
    np.write()
