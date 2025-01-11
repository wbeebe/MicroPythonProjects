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
import gc
import os
import platform
import binascii
import machine as ma
import time
import SSD1306
import display_tools
import webpage
import ntptime

print(f"\n MEM FREE: {gc.mem_free():,} BYTES")
UNAME = os.uname().sysname.upper()
stat_vfs = os.statvfs('/')
fs_total = stat_vfs[0] * stat_vfs[2]
fs_free  = stat_vfs[0] * stat_vfs[3]
fs_used  = fs_total - fs_free
print(f" FS TOTAL: {fs_total:,} BYTES")
print(f" FS  FREE: {fs_free:,} BYTES")
print(f" FS  USED: {fs_used:,} BYTES")
print(f" PLATFORM: {platform.platform()}")

UNIQUE_ID = binascii.hexlify(ma.unique_id()).decode('ascii').upper()
print(f"      UID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(f"     SSID: {SSID}")
print(f" CPU FREQ: {ma.freq():,} Hz")
#
# Set up to use on-board LED
#
can_flash = True
led = ma.Pin("LED", ma.Pin.OUT)
led.value(0)

def led_timer_callback(t):
    if can_flash:
        led.toggle()

led_timer = ma.Timer()
led_timer.init(freq=1, mode=ma.Timer.PERIODIC, callback=led_timer_callback)
#
# Set up I2C. Needed for SSD1306 OLED display control.
#
SDA_PIN = ma.Pin(4) # Blue wire
SCL_PIN = ma.Pin(5) # Yellow wire
I2C = ma.SoftI2C(scl=SCL_PIN, sda=SDA_PIN, freq=250000)
#
# Set up SSD1306 OLED display.
#
display = SSD1306.SSD1306_I2C(I2C)
display.fill(0)
display_tools.do_graphics(display, platform.platform(), SSID)

def one_shot_callback(t):
    display.fill(0)
    display.show()

one_shot = ma.Timer()
#
# Turn off OLED after 60 seconds to preserve display.
#
one_shot.init(period=120000, mode=ma.Timer.ONE_SHOT, callback=one_shot_callback)

#
# Set up WiFi and controlling web page.
#
import network
import socket
import settings

wifi = network.WLAN(network.STA_IF)
network.hostname(SSID)
wifi.active(True)
wifi.connect(settings.AP_SSID, settings.AP_PWRD)

while wifi.isconnected() == False:
    time.sleep_ms(1000)

attempts = 10
while attempts > 0:
    try:
        ntptime.settime()
        attempts = 0
    except Exception as te:
        print(te)
        time.sleep_ms(1000)
        attempts -= 1

ip = wifi.ifconfig()[0]
print(f"     WIFI: {ip}")
display.text(str(ip), 0, 36, 1)
display.show()

address = (ip, 80)
connection = socket.socket()
connection.bind(address)
connection.listen(4)

print(f"     WIFI: Ready {ip}")

while True:
    client = connection.accept()[0]
    request = str(client.recv(2048))
    if 'LED+OFF=OFF' in request:
        led.value(0)
        can_flash = False
    if 'LED+ON=ON' in request:
        can_flash = True
    if 'DISPLAY+ON=ON' in request:
        display_tools.do_graphics(display, platform.platform(), SSID)
        display.text(str(ip), 0, 36, 1)
        display.show()
        one_shot.init(period=120000, mode=ma.Timer.ONE_SHOT, callback=one_shot_callback)
    if 'DISPLAY+OFF=OFF' in request:
        display.fill(0)
        display.show()

    client.send(webpage.webpage(SSID))
    client.close()
