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

# This is the Simple HTTP Server.
# It has HTML/CSS text intermixed with Python code.
# It provides very limited functionality.
# SSD1396 OLED Display

import binascii
import machine
import os
import platform
import usocket
import _thread
import time
import gc
import network
from network import WLAN
from machine import RTC, Pin, SoftI2C

import ssd1306
import config

UNAME = os.uname()[-1].split(' ')[0]
UNIQUE_ID = binascii.hexlify(machine.unique_id()).decode('ascii').upper()
SSID = UNAME + '-' + UNIQUE_ID[-4:]

class SimpleHttpServer:
    do_action = None
    i2c = SoftI2C(scl=machine.Pin(config.SCL_PIN), sda=machine.Pin(config.SDA_PIN))
    display = None
    style_str = """
        <style>
        body {font-family: sans-serif;margin: 20px;}
        button {
            font-size: 300%;
            font-weight: normal;
            display: inline-block;
            margin: 5px;
            padding: 20px 60px;
            width: 99%;
            height: 100px;
            justify-content: center;
            align-items: center;
            text-decoration: none;
            color: #ffffff;
            background-color: #556B2F;
            border: none;
            border-radius: 0px;
            outline: none;
        }
        hr {border: 0;height: 2px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));}
        h1 {font-size: 300%;color: #D35F8D;text-align: center;}
        h2 {font-size: 250%;color: #5FA3D3;padding-left: 15px;}
        </style>
    """

    def __init__(self, do_action):
        self.do_action = do_action
        self.do_action(config.LED_OFF)
        self.name = os.uname()[-1].split(' ')[-1]
        self.display = ssd1306.SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, self.i2c, config.OLED_ADDR)
        self.display.fill(0)
        self.display.show()
        gc.enable()
        

    def display_show_one_line(self, msg):
        self.display.fill(0)
        self.display.line(msg,1)
        self.display.show()

    def client_thread(self, clientsocket):
        global SSID

        try:
            received = clientsocket.recv(8192)
        except:
            print("WEBSERVER: EXCEPTION ON RECV")
            clientsocket.close()
            return

        # If received has 0 bytes then the other end closed the connection.
        #
        if len(received) == 0:
            print("[5] WEBSERVER: ZERO LENGTH RECEIVED")
            clientsocket.close()
            return

        print("[5] WEBSERVER: RECEIVED DATA {:,} BYTES".format(len(received)))

        print("[6] WEBSERVER: PARSE")
        # Parse the recieved data and perform any given actions.
        #
        received_str = str(received)
        #
        # Uncomment the following for raw debugging purposes. Lots of output.
        #
        #print("WEBSERVER: DATA", received_str)

        # Send out the webpage.
        #
        clientsocket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection:close \r\n\r\n")
        clientsocket.send("<html><head><title>{}</title>".format(SSID))
        clientsocket.send(self.style_str)
        clientsocket.send("</head><body>")
        clientsocket.send("<h1>{}</h1>".format(SSID))

        # Start parsing the request, performing the various actions.
        # If there is no defined actions for the request, tell the user.
        #
        if "GET / " in received_str:
            clientsocket.send(
                "<hr/>"
                "<a href='/func1'><button style='background-color: #DC143C'>Red</button></a>"
                "<a href='/func2'><button style='background-color: #228B22'>Green</button></a>"
                "<a href='/func3'><button style='background-color: #4169E1'>Blue</button></a>"
                "<a href='/func4'><button style='background-color: #808080'>Cycle</button></a>"
                "<a href='/func5'><button style='background-color: #404040'>OFF</button></a>"
                "<a href='/func6'><button style='background-color: #402000'>Test OLED</button></a>"
                )
        elif "GET /func1 " in received_str:
            print("WEBSERVER: FUNC 1")
            clientsocket.send("<h1>LED Red</h1>")
            self.display_show_one_line('LED Red')
            self.do_action(config.LED_RED)
        elif "GET /func2 " in received_str:
            print("WEBSERVER: FUNC 2")
            clientsocket.send("<h1>LED Green</h1>")
            self.display_show_one_line('LED Green')
            self.do_action(config.LED_GREEN)
        elif "GET /func3 " in received_str:
            print("WEBSERVER: FUNC 3")
            clientsocket.send("<h1>LED Blue</h1>")
            self.display_show_one_line('LED Blue')
            self.do_action(config.LED_BLUE)
        elif "GET /func4 " in received_str:
            print("WEBSERVER: FUNC 4")
            clientsocket.send("<h1>LED Cycle</h1>")
            self.display_show_one_line('')
            self.do_action(config.LED_CYCLE)
        elif "GET /func5 " in received_str:
            print("WEBSERVER: FUNC 5")
            clientsocket.send("<h1>LED OFF</h1>")
            self.display_show_one_line('')
            self.do_action(config.LED_OFF)
        elif "GET /func6 " in received_str:
            print("WEBSERVER: FUNC 6")
            clientsocket.send("<h1>Test OLED</h1>")
            self.display.test_oled()
        else:
            clientsocket.send("<h1>Undefined Action</h1>" + received_str)

        print("[7] WEBSERVER: FOOTER")
        clientsocket.send("<a href='/'><button style='background-color: #007C80'><em>Home</em></button></a>")
        clientsocket.send("<hr/>")
        clientsocket.send("<h2>Memory Free: {:,} bytes</h2>".format(gc.mem_free()))
        clientsocket.send("<h2>{}</h2>".format(platform.platform()))
        clientsocket.send("</body></html>")

        gc.collect()
        clientsocket.close()

    def run(self):
        global SSID
        # create as an access point
        #
        wlan = WLAN(network.AP_IF)
        wlan.active(True)

        # configure as an access point
        #
        print("[1] WEBSERVER:",SSID)
        wlan.config(essid=SSID)
        while wlan.active() is False:
            pass
        wlan.ifconfig(('192.168.1.2','255.255.255.0','192.168.1.1','8.8.8.8'))

        # Set up server socket to read client responses from web pages
        #
        serversocket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        serversocket.bind(("192.168.1.2", 80))
        print("[2] WEBSERVER: BIND")

        # Listen argument defines the maximum connections at the same time.
        #
        serversocket.listen(8)

        while True:
            print("[3] WEBSERVER: ACCEPT")
            #try:
            (clientsocket, address) = serversocket.accept()
                #
                # Start a new thread to handle the client
                #
            print("\n[4] WEBSERVER: START_NEW_THREAD")
                #_thread.start_new_thread(self.client_thread, (clientsocket, ))
            self.client_thread(clientsocket)
            print("[8] WEBSERVER: THREAD_RETURN")
            #except:
            #    print("[3] WEBSERVER: CONNECTION ERROR")
                #serversocket.close()
                #serversocket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
                #serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
                #serversocket.bind(("192.168.1.2", 80))
