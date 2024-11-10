"""
   This code is licensed under Apache Apache Version 2.0, January 2004

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
"""
import machine  as ma
import neopixel as neo
import time     as ti
import config
import devices

devices.cycle_colors()

from webserver import WebServer
web = WebServer(SSID)
web.run()
