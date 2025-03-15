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
import binascii
import machine
import os
import platform
import socket
import time
import esp
import gc
import network
import ntptime
import esp32
from network import WLAN
from machine import Pin, SoftI2C

import config
import devices
import settings

def formatted_time():
    dayname = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",]

    monthname = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December" ]

    now = time.localtime(time.time() + (-4 * 3600))
    day_name = dayname[now[6]]
    month_day = now[2]
    month_name = monthname[now[1]-1]
    year = now[0]

    hour = now[3]

    if hour < 11:
        am_pm = 'AM'
        if hour == 0:
            hour = 12
    else:
        am_pm = 'PM'
        if hour > 12:
            hour -= 12

    minutes = now[4]

    return f"{hour}:{minutes:02} {am_pm} - {day_name} {month_day} {month_name} {year}"

def webpage(SSID):
    try:
        vsf2 = esp32.Partition('vfs2')
        vfs2_size = vsf2.info()[3]
    except:
        vfs2_size = 0;
    html = f"""
    <html><head><title>{SSID}</title>
    <style>
    html{{
        font-family: sans-serif;
        background-color: #FFFFFF;
        display: inline-block;
        margin: 0px auto;
        }}
    button {{
        font-size: 500%;
        font-weight: normal;
        display: inline-block;
        margin: 5px;
        padding: 20px 60px;
        width: 99%;
        height: 150px;
        justify-content: center;
        align-items: center;
        text-decoration: none;
        color: #ffffff;
        border: none;
        border-radius: 15px;
        outline: none;
        }}
    .button-red {{
        background-color: #DC143C;
    }}
    .button-green {{
        background-color: #228B22;
    }}
    .button-blue {{
        background-color: #4169E1;
    }}
    .button-gray {{
        background-color: #808080;
    }}
    .button-off {{
        background-color: #404040;
    }}
    hr {{
        border: 0;height: 2px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));
        }}
    h1 {{font-size: 500%;color: #D35F8D;text-align: center;}}
    h2 {{font-size: 200%;color: #5FA3D3;padding-left: 15px;}}
    </style>
    </head>
    <body>
    <h1>{SSID}</h1>
    <form accept-charset="utf-8" method="POST">
    <button class='button-red'   name="RED"   value="ON">Red</button>
    <button class='button-green' name="GREEN" value="ON">Green</button>
    <button class='button-blue'  name="BLUE"  value="ON">Blue</button>
    <button class='button-gray'  name="CYCLE" value="ON">Cycle</button>
    </form>
    <hr />
    <h2>{formatted_time()}</h2>
    <h2>{config.version_name}<br/>
    Last built with {config.compiler}<br />
    Last built on {config.build_date}</h2>
    <h2>Flash size: {esp.flash_size():,} bytes<br/>
    vfs2 size: {vfs2_size:,} bytes<br/>
    Memory free: {gc.mem_free():,} bytes</h2>
    </body>
    </html>
    """
    return html

class WebServer:
    SSID = None

    def __init__(self):
        self.name = os.uname().machine.split(' ')[-1]
        self.SSID = self.name + '-' + binascii.hexlify(machine.unique_id()).decode('ascii').upper()[-4:]
        print(" "+self.SSID)
        gc.enable()

    def run(self):
        # Join an access point
        #
        wlan = WLAN(network.STA_IF)
        network.hostname(self.SSID)
        wlan.active(True)
        wlan.connect(settings.AP_SSID, settings.AP_PASSWORD)
        
        while not wlan.isconnected():
            time.sleep_ms(2000)

        print(" WIFI connected")

        attempts = 10
        while attempts > 0:
            try:
                ntptime.settime()
                attempts = 0
                print(f" WIFI: NTP Successful")
                print(f"  NTP: {formatted_time()}")
            except Exception as te:
                print(te)
                print(f" WIFI: NTP {attempts}")
                time.sleep_ms(1000)
                attempts -= 1

        ip = wlan.ifconfig()[0]
        print(" "+ip)
        address = (ip, 80)
        connection = socket.socket()
        connection.bind(address)
        connection.listen(4)

        while True:
            client_connect, client_addr = connection.accept()
            #print(f" WIFI client {str(client_addr)}")
            request = str(client_connect.recv(4096))
            #
            # If received has 0 bytes then the other end closed the connection.
            #
            #if len(request) == 0:
            #    client_connect.close()
            #    pass

            # Parse the request, performing various actions.
            #
            if "RED=ON" in request:
                devices.toggle_led_color(devices.LED_RED)
            elif "GREEN=ON" in request:
                devices.toggle_led_color(devices.LED_GREEN)
            elif "BLUE=ON" in request:
                devices.toggle_led_color(devices.LED_BLUE)
            elif "CYCLE=ON" in request:
                devices.cycle_colors()

            client_connect.send(webpage(self.SSID))
            gc.collect()

            # Close the socket and terminate the thread
            client_connect.close()
