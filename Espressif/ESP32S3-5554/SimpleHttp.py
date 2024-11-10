"""
This is the Simple HTTP Server.
It has HTML/CSS text intermixed with Python code.
It provides very limited functionality.
SSD1306 OLED Display
"""

import usocket
import _thread
import time
import gc
import network
from network import WLAN

import ssd1306
import config

class SimpleHttpServer:

    def __init__(self, SSID, SOFT_I2C, do_action, PLATFORM):
        self.i2c = SOFT_I2C
        self.SSID = SSID
        self.platform = PLATFORM
        self.do_action = do_action
        self.display = ssd1306.SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, self.i2c, config.OLED_ADDR)
        self.display.fill(0)
        self.display.show()
        gc.enable()

    def test_oled(self):
        for i in range(1, config.OLED_LINE_MAX + 1):
            self.display.fill(0)
            self.display.line(f"LINE {i} ----+----", i)
            self.display.show()
            time.sleep_ms(500)

        self.display.fill(0)
        self.display.show()

    def client_thread(self, clientsocket):
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
            clientsocket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection:close \r\n\r\n")
            clientsocket.send("<html><head><title>" + self.SSID + "</title>")
            clientsocket.send(
                "<style>"
                "body {font-family: sans-serif;margin: 20px;}"
                "button {"
                "font-size: 300%;"
                "font-weight: bold;"
                "display: inline-block;"
                "margin: 5px;"
                "padding: 20px 60px;"
                "width: 99%;"
                "height: 150px;"
                "justify-content: center;"
                "align-items: center;"
                "text-decoration: none;"
                "color: #ffffff;"
                "background-color: #556B2F;"
                "border: none;"
                "border-radius: 0px;"
                "outline: none;}"
                "hr {border: 0;height: 2px;"
                "background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));}"
                "h1 {font-size: 300%;color: #D35F8D;text-align: center;}"
                "h2 {font-size: 250%;color: #5FA3D3;padding-left: 15px;}"
                "</style>"
                "</head><body>")
            clientsocket.send("<h1>" + self.SSID + "</h1>")

            # Start parsing the request, performing the various actions.
            # If there is no defined actions for the request, tell the user.
            #
            if "GET / " in received_str:
                clientsocket.send(
                    "<hr/>"
                    "<a href='/func1'><button style='background-color: #DC143C'>LED Red</button></a>"
                    "<a href='/func2'><button style='background-color: #228B22'>LED Green</button></a>"
                    "<a href='/func3'><button style='background-color: #4169E1'>LED Blue</button></a>"
                    "<a href='/func4'><button style='background-color: #808080'>LED Cycle</button></a>"
                    "<a href='/func5'><button style='background-color: #404040'>LED OFF</button></a>"
                    "<a href='/func6'><button style='background-color: #402000'>Test OLED</button></a>"
                    )
            elif "GET /func1 " in received_str:
                clientsocket.send("<h1>LED Red</h1>")
                self.display.fill(0)
                self.display.line('LED Red',1)
                self.display.show()
                self.do_action(config.LED_RED)
            elif "GET /func2 " in received_str:
                clientsocket.send("<h1>LED Green</h1>")
                self.display.fill(0)
                self.display.line('LED Green',1)
                self.display.show()
                self.do_action(config.LED_GREEN)
            elif "GET /func3 " in received_str:
                clientsocket.send("<h1>LED Blue</h1>")
                self.display.fill(0)
                self.display.line('LED Blue',1)
                self.display.show()
                self.do_action(config.LED_BLUE)
            elif "GET /func4 " in received_str:
                clientsocket.send("<h1>LED Cycle</h1>")
                self.display.fill(0)
                self.display.show()
                self.do_action(config.LED_CYCLE)
            elif "GET /func5 " in received_str:
                clientsocket.send("<h1>LED OFF</h1>")
                self.display.fill(0)
                self.display.show()
                self.do_action(config.LED_OFF)
            elif "GET /func6 " in received_str:
                clientsocket.send("<h1>Test OLED</h1>")
                self.test_oled()
            else:
                clientsocket.send("<h1>Undefined Action</h1>" + received_str)

            clientsocket.send("<a href='/'><button style='background-color: #007C80'><em>Home</em></button></a>")
            clientsocket.send("<HR/>")
            clientsocket.send(f"<h2>Memory Free: {gc.mem_free():,} bytes</h2>")
            clientsocket.send("<h2>" + self.platform + "</h2>")
            clientsocket.send("</body></html>")
            gc.collect()

            # Close the socket and terminate the thread
            clientsocket.close()

        time.sleep_ms(500)

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
            _thread.start_new_thread(self.client_thread, (clientsocket, ))
        serversocket.close()
