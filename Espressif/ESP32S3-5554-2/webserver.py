"""
This is the Simple HTTP Server.
It has HTML/CSS text intermixed with Python code.
It provides very limited functionality.
SSD1306 OLED Display
"""

import os
import usocket
import _thread
import time
import esp
import gc
import network
from network import WLAN

import ssd1306
import devices

def webpage(SSID, PLATFORM):
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
        background-color: #556B2F;
        border: none;
        border-radius: 0px;
        outline: none;
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
    <button style='background-color: #DC143C' name="RED"   value="ON">Red</button>
    <button style='background-color: #228B22' name="GREEN" value="ON">Green</button>
    <button style='background-color: #4169E1' name="BLUE"  value="ON">Blue</button>
    <button style='background-color: #404040' name="OFF"   value="OFF">OFF</button>
    <button style='background-color: #808080' name="CYCLE" value="ON">Cycle</button>
    <button style='background-color: #402000' name="OLED"  value="ON">OLED Test</button>
    </form>
    <hr />
    <h2>{PLATFORM}<br/>
    Last built: {os.uname().version.split(' ')[-1]}</h2>
    <h2>Flash Size: {esp.flash_size():,} bytes<br/>
    Memory Free: {gc.mem_free():,} bytes</h2>
    </body>
    </html>
    """
    return html

class WebServer:

    def __init__(self, SSID, SOFT_I2C, PLATFORM):
        self.i2c = SOFT_I2C
        self.SSID = SSID
        self.platform = PLATFORM
        self.display = ssd1306.SSD1306_I2C(devices.OLED_WIDTH, devices.OLED_HEIGHT, self.i2c, devices.OLED_ADDR)
        self.display.fill(0)
        self.display.show()
        gc.enable()

    def server_thread(self, clientsocket):
        try:
            received = clientsocket.recv(4096)
        except:
            clientsocket.close()
            return

        # If received has 0 bytes then the other end closed the connection.
        #
        if len(received) == 0:
            clientsocket.close()
            return
        else:
            # Parse the recieved data and perform any given actions.
            #
            received_str = str(received)
            #
            # Uncomment the following for raw debugging purposes. Lots of output.
            #
            #print("Received: {}".format(received_str))

            # Send out the common webpage header for all pages.
            #
            clientsocket.send(webpage(self.SSID, self.platform))

            # Start parsing the request, performing the various actions.
            # If there is no defined actions for the request, tell the user.
            #
            if "RED=ON" in received_str:
                self.display.show_only_one_line('LED Red')
                devices.set_led_color(devices.LED_RED)
            elif "GREEN=ON" in received_str:
                self.display.show_only_one_line('LED Green')
                devices.set_led_color(devices.LED_GREEN)
            elif "BLUE=ON" in received_str:
                self.display.show_only_one_line('LED Blue')
                devices.set_led_color(devices.LED_BLUE)
            elif "OFF=OFF" in received_str:
                self.display.show_only_one_line('')
                devices.set_led_color(devices.LED_OFF)
            elif "CYCLE=ON" in received_str:
                self.display.show_only_one_line('')
                devices.cycle_colors()
            elif "OLED=ON" in received_str:
                self.display.test_oled()
            gc.collect()

            # Close the socket and terminate the thread
            clientsocket.close()

    def run(self):
        wlan = WLAN(network.AP_IF)
        wlan.active(True)
        wlan.config(essid=self.SSID)
        wlan.ifconfig(('192.168.1.2','255.255.255.0','192.168.1.1','8.8.8.8'))

        serversocket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        serversocket.bind(("192.168.1.2", 80))
        serversocket.listen(1)

        while True:
            (clientsocket, address) = serversocket.accept()
            _thread.start_new_thread(self.server_thread, (clientsocket, ))
        serversocket.close()
