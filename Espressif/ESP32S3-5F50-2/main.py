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
import machine  as ma
import neopixel as neo
import time     as ti
import _thread
import config
import os
import esp
import gc

print(f" {config.version_name}")
print(f" Built with {config.compiler}")
print(f" Built on {config.build_date}")
print(f" Flash size {esp.flash_size():,} bytes")
print(f" Memory free {gc.mem_free():,} bytes.")

name = os.uname().machine.split(' ')[-1]
if name is "ESP32S3":
    pinnum = 48
elif name is 'ESP32':
    # Setup specifically for Adafruit Huzzah ESP32 V2.
    # Pin 0 is the data pin to the NeoPixel,
    # Pin 2 is the power pin that must be set as an
    # an output and on, or high.
    #
    pinnum = 0
    #
    # Turn on the power for the NeoPixel.
    #
    pwr = ma.Pin(2, ma.Pin.OUT)
    pwr.value(1)
else:
    pinnum = 8

np = neo.NeoPixel(ma.Pin(pinnum), 1)

neopixel_colors = [
    (64, 0, 0),  # red
    (0, 64, 0),  # green
    (0, 0, 64),  # blue
    (64, 32, 0), # orange
    (0, 64, 64), # cyan
    (0, 0, 0)    # black
    ]

def cycle_colors():
    for color in neopixel_colors:
        np[0] = color
        np.write()
        ti.sleep_ms(400)
    np[0] = neopixel_colors[-1]
    np.write()

def do_action(action_to_do):
    if action_to_do == config.LED_CYCLE:
        cycle_colors();
    else:
        np[0] = neopixel_colors[action_to_do]
        np.write()

cycle_colors()

from webserver import WebServer
web = WebServer(do_action)
web.run()
