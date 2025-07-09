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

import platform
from machine import Timer
import time
import mqtt_tools as mqtt

display = None
ssid = None
ip = None

def do_graphics(_display, _ssid, _ip):
    global display, ssid, ip

    display = _display
    ssid = _ssid
    ip = _ip
    #
    # Display the official MicroPython logo
    #
    display.framebuf.fill_rect(0, 0, 32, 32, 1)
    display.framebuf.fill_rect(2, 2, 28, 28, 0)
    display.framebuf.vline(9, 8, 22, 1)
    display.framebuf.vline(16, 2, 22, 1)
    display.framebuf.vline(23, 8, 22, 1)
    display.framebuf.fill_rect(26, 24, 2, 4, 1)
    #
    # Print some identifying text with the graphics.
    #
    display.text('VER ', 40, 0, 1)
    display.text(platform.platform().split('-')[1], 72, 0, 1)
    if mqtt.mqttClient is not None:
        display.text(f"MQTT {mqtt.mqtt_msg_count}", 40, 10, 1)
    display.text(ssid, 0, 36, 1)
    display.text(str(ip), 0, 46, 1)
    now = time.localtime(time.time() + (-4 * 3600))
    year = now[0]
    month = now[1]
    day = now[2]
    hour = now[3]
    minutes = now[4]
    display.text(f"{month:02}/{day:02}/{year} {hour:02}:{minutes:02}", 0, 56, 1)
    display.show()

_show_display = True

def timer_callback(t):
    global display, _show_display
    _show_display = False
    display.fill(0)
    display.show()

def setup_display_blank_timer():
    timer = Timer(2)
    timer.init(period=60000, mode=Timer.ONE_SHOT, callback=timer_callback)

def toggle_display_on_off():
    global display, ssid, ip, _show_display
    
    if display is None:
        return

    _show_display = not _show_display

    if _show_display:
        do_graphics(display, ssid, ip)
        setup_display_blank_timer()
    else:
        display.fill(0)
        display.show()
