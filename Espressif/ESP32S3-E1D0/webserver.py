"""
   This code is licensed under Apache Version 2.0, January 2004

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
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
from network import WLAN
from machine import Pin, SoftI2C

import ssd1306
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

    _24_to_12 = [ 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,  # AM
                  12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ] # PM

    if now[3] < 11:
        am_pm = 'AM'
    else:
        am_pm = 'PM'

    hour = _24_to_12[now[3]]
    minutes = now[4]

    return f"{hour}:{minutes:02} {am_pm} - {day_name} {month_day} {month_name} {year}"

def webpage(SSID):
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
        border-radius: 5px;
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
    <button class='button-off'   name="OFF"   value="OFF">Off</button>
    <button class='button-gray'  name="CYCLE" value="ON">Cycle</button>
    </form>
    <hr />
    <h2>{formatted_time()}</h2>
    <h2>{' '.join(platform.platform().split('-')[0:3])}<br/>
    Last built on {os.uname().version.split(' ')[-1]}</h2>
    <h2>Flash size: {esp.flash_size():,} bytes<br/>
    Memory free: {gc.mem_free():,} bytes</h2>
    </body>
    </html>
    """
    return html

class WebServer:
    #i2c = SoftI2C(scl=machine.Pin(devices.SCL_PIN), sda=machine.Pin(devices.SDA_PIN))
    display = None
    SSID = None

    def __init__(self):
        self.name = os.uname().machine.split(' ')[-1]
        self.SSID = self.name + '-' + binascii.hexlify(machine.unique_id()).decode('ascii').upper()[-4:]
        print(" "+self.SSID)
        #self.display = ssd1306.SSD1306_I2C(devices.OLED_WIDTH, devices.OLED_HEIGHT, self.i2c, devices.OLED_ADDR)
        #self.display.fill(0)
        #self.display.show()
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

        attempt_limit = 10
        attempt_count = 1
        while attempt_limit > 0:
            try:
                ntptime.settime()
                attempt_limit = 0
                print(f" WIFI: NTP Connection Successful")
                print(f" Time: {formatted_time()}")
            except Exception as te:
                print(te)
                print(f" WIFI: NTP Connection Attempt #{attempt_count}")
                time.sleep_ms(1000)
                attempt_limit -= 1
                attempt_count += 1

        ip = wlan.ifconfig()[0]
        print(" "+ip)
        address = (ip, 80)
        connection = socket.socket()
        connection.bind(address)
        connection.listen(4)

        while True:
            client_connect, client_addr = connection.accept()
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
                #self.display.show_only_one_line('LED Red')
                devices.set_led_color(devices.LED_RED)
            elif "GREEN=ON" in request:
                #self.display.show_only_one_line('LED Green')
                devices.set_led_color(devices.LED_GREEN)
            elif "BLUE=ON" in request:
                #self.display.show_only_one_line('LED Blue')
                devices.set_led_color(devices.LED_BLUE)
            elif "OFF=OFF" in request:
                #self.display.show_only_one_line('')
                devices.set_led_color(devices.LED_OFF)
            elif "CYCLE=ON" in request:
                #self.display.show_only_one_line('')
                devices.cycle_colors()

            client_connect.send(webpage(self.SSID))
            gc.collect()

            # Close the socket and terminate the thread
            client_connect.close()