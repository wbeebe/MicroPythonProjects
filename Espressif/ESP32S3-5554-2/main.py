import machine  as ma
import neopixel as neo
import time     as ti
import config
import os

name = os.uname().machine.split(' ')[-1]
from webserver import WebServer
web = WebServer(SSID, SOFT_I2C, PLATFORM)
web.run()
