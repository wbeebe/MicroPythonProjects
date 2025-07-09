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

import socket
import time
import gc
import ntptime
import network
from network import WLAN

import config
import devices
import display_tools
import mqtt_tools as mqtt
import time_tools as ttools
import ht16k33_tools as htools
import webpage as web
import settings

class WebServer:
    SSID = None
    do_action = None

    def __init__(self, _SSID, _DISPLAY):
        self.SSID = _SSID
        self.DISPLAY = _DISPLAY
        gc.enable()

    def run(self):
        wlan = WLAN(network.STA_IF)
        network.hostname(self.SSID)
        wlan.active(True)

        wlan.connect(settings.AP_SSID, settings.AP_PASSWORD)

        while not wlan.isconnected():
            time.sleep_ms(2000)

        print("      WIFI: Connected")

        ip = wlan.ifconfig()[0]
        print(f"      WIFI: {ip}")

        attempts = 1
        while attempts < 10:
            try:
                print(f"      WIFI: NTP Connection Attempt #{attempts}")
                ntptime.settime()
                attempts = 10
                print(f"      WIFI: NTP Connection Successful")
                print(f"      DATE: {ttools.formatted_time()}")
                htools.start_clock();
            except Exception as ntp_time_exception:
                print(ntp_time_exception)
                time.sleep_ms(1000)
                attempts += 1

        mqtt.broker_connect(self.SSID)

        address = (ip, 80)
        connection = socket.socket()
        connection.bind(address)
        connection.listen(4)

        if self.DISPLAY is not None:
            display_tools.do_graphics(self.DISPLAY, self.SSID, ip)
            display_tools.setup_display_blank_timer()

        while True:
            try:
                (clientsocket, address) = connection.accept()
                received = clientsocket.recv(4096)
                received_str = str(received)
                clientsocket.send(web.page(self.SSID, self.DISPLAY, mqtt.mqttClient))

                # Parse the request, performing the associated actions.
                #
                if "RED=ON" in received_str:
                    state = devices.toggle_led_color(devices.LED_RED)
                    mqtt_message = f"\"COLOR\":\"RED\",\"STATE\":\"{state}\""
                    mqtt.publish("NEOP", mqtt_message)
                elif "GREEN=ON" in received_str:
                    state = devices.toggle_led_color(devices.LED_GREEN)
                    mqtt_message = f"\"COLOR\":\"GREEN\",\"STATE\":\"{state}\""
                    mqtt.publish("NEOP", mqtt_message)
                elif "BLUE=ON" in received_str:
                    state = devices.toggle_led_color(devices.LED_BLUE)
                    mqtt_message = f"\"COLOR\":\"BLUE\",\"STATE\":\"{state}\""
                    mqtt.publish("NEOP", mqtt_message)
                elif "CYCLE=ON" in received_str:
                    devices.cycle_colors()
                elif "OLED=ON" in received_str:
                    display_tools.toggle_display_on_off()
                elif "MQTT=ON" in received_str:
                    mqtt.report()

                clientsocket.close()

            except Exception as wifi_exception:
                print(wifi_exception)

            gc.collect()
