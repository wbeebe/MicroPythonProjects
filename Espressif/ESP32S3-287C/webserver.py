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
import _thread
import time
import esp
import gc
import network
from network import WLAN
from machine import Pin, SoftI2C

import ssd1306
import devices

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
        self.name = os.uname()[-1].split(' ')[-1]
        self.SSID = self.name + '-' + binascii.hexlify(machine.unique_id()).decode('ascii').upper()[-4:]
        #self.display = ssd1306.SSD1306_I2C(devices.OLED_WIDTH, devices.OLED_HEIGHT, self.i2c, devices.OLED_ADDR)
        #self.display.fill(0)
        #self.display.show()
        gc.enable()

    def server_thread(self, clientsocket):
        received = clientsocket.recv(4096)

        # If received has 0 bytes then the other end closed the connection.
        #
        if len(received) == 0:
            clientsocket.close()
            return
        else:
            # Parse the recieved data and perform any given actions.
            #
            received_str = str(received)
            #print(received_str)
            #print()
            #
            clientsocket.send(webpage(self.SSID))
            # Parse the request, performing various actions.
            #
            if "RED=ON" in received_str:
                #self.display.show_only_one_line('LED Red')
                devices.set_led_color(devices.LED_RED)
            elif "GREEN=ON" in received_str:
                #self.display.show_only_one_line('LED Green')
                devices.set_led_color(devices.LED_GREEN)
            elif "BLUE=ON" in received_str:
                #self.display.show_only_one_line('LED Blue')
                devices.set_led_color(devices.LED_BLUE)
            elif "OFF=OFF" in received_str:
                #self.display.show_only_one_line('')
                devices.set_led_color(devices.LED_OFF)
            elif "CYCLE=ON" in received_str:
                #self.display.show_only_one_line('')
                devices.cycle_colors()
            gc.collect()

            # Close the socket and terminate the thread
            clientsocket.close()

        #time.sleep_ms(500)

    def run(self):
        # create as an access point
        #
        wlan = WLAN(network.AP_IF)
        wlan.active(True)

        # configure as an access point
        #
        print(self.SSID)
        wlan.config(essid=self.SSID)
        wlan.ifconfig(('192.168.1.2','255.255.255.0','192.168.1.1','8.8.8.8'))

        # Set up server socket to read client responses from web pages
        #
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(("192.168.1.2", 80))

        # Listen argument defines the maximum connections at the same time.
        #
        serversocket.listen(4)

        while True:
            (clientsocket, address) = serversocket.accept()
            # Start a new thread to handle the client
            #
            _thread.start_new_thread(self.server_thread, (clientsocket, ))

        serversocket.close()
