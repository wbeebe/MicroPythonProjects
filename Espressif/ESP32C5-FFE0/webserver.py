"""
Copyright 2025, 2026 William H. Beebe, Jr.

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
import display_tools
import mqtt_tools as mqtt
import time_tools as ttools
import webpage as web
import settings

class WebServer:
    SSID = None
    do_action = None

    def __init__(self, _SSID, _DISPLAY, _DHT20):
        self.SSID = _SSID
        self.DISPLAY = _DISPLAY
        self.DHT20 = _DHT20
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
            except Exception as ntp_time_exception:
                print(f"      WIFI: NTP EXCEPTION {ntp_time_exception}")
                time.sleep_ms(1000)
                attempts += 1

        mqtt.broker_connect(self.SSID, self.DHT20)

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
                clientsocket.send(web.page(self.SSID, self.DISPLAY, mqtt.mqttClient, self.DHT20))

                # Parse the request, performing the associated actions.
                #
                if "RTH=READ" in received_str:
                    self.DHT20.read_temperature_humidity()
                elif "OLED=ON" in received_str:
                    display_tools.toggle_display_on_off()
                elif "MQTT=ON" in received_str:
                    mqtt.report()

                clientsocket.close()

            except Exception as wifi_exception:
                print(wifi_exception)

            gc.collect()
