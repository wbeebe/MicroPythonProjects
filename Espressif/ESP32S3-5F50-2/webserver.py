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
import _thread
import time
import esp
import gc
import network
from network import WLAN
from machine import RTC

import config

def webpage(SSID):
    version_name = ' '.join(platform.platform().split('-')[0:3])
    compiler = platform.platform().split('-')[4]
    html = f"""
    <html><head><title>{SSID}</title>
    <style>
    body {{font-family: sans-serif;margin: 20px;}}
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
        background-color: #20A020;
        }}
    .button-blue {{
        background-color: #4080E0;
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
    <hr />
    <form accept-charset="utf-8" method="POST">
    <button class='button-red'   name="RED"   value="ON">Red</button>
    <button class='button-green' name="GREEN" value="ON">Green</button>
    <button class='button-blue'  name="BLUE"  value="ON">Blue</button>
    <button class='button-off'   name="OFF"   value="OFF">OFF</button>
    <button class='button-gray'  name="CYCLE" value="ON">Cycle</button>
    </form>
    <hr />
    <h2>{version_name}<br />
    Last built with {compiler}<br />
    Last built on {os.uname().version.split(' ')[-1]}</h2>
    <h2>Flash Size: {esp.flash_size():,} bytes<br />
    Memory Free: {gc.mem_free():,} bytes</h2>
    </body>
    </html>
    """
    return html

class WebServer:
    SSID = None
    do_action = None

    def __init__(self, do_action):
        self.do_action = do_action
        self.name = os.uname()[-1].split(' ')[-1]
        self.SSID = self.name + '-' + binascii.hexlify(machine.unique_id()).decode('ascii').upper()[-4:]
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
            # Start parsing the request, performing the various actions.
            # If there is no defined actions for the request, tell the user.
            #
            if "RED=ON" in received_str:
                self.do_action(config.LED_RED)
            elif "GREEN=ON" in received_str:
                self.do_action(config.LED_GREEN)
            elif "BLUE=ON" in received_str:
                self.do_action(config.LED_BLUE)
            elif "CYCLE=ON" in received_str:
                self.do_action(config.LED_CYCLE)
            elif "OFF=OFF" in received_str:
                self.do_action(config.LED_OFF)
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
        print(f" SSID = {self.SSID}")
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
