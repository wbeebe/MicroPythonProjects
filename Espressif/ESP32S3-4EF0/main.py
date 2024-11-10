import machine  as ma
import neopixel as neo
import time     as ti
import _thread
import config

import os
print(', '.join(os.uname()))

import platform
print(platform.platform())

# For ESP32S3
pinnum = 48 
np = neo.NeoPixel(ma.Pin(pinnum), 1)

neopixel_colors = [
    (64, 0, 0),  # red
    (0, 64, 0),  # green
    (0, 0, 64),  # blue
    (64, 32, 0), # orange
    (0, 64, 64), # cyan
    (0, 0, 0)    # black
    ]

def cycle_colors():
    for color in neopixel_colors:
        np[0] = color
        np.write()
        ti.sleep_ms(400)
    np[0] = neopixel_colors[-1]
    np.write()

def do_action(action_to_do):
    if action_to_do < config.LED_CYCLE:
        np[0] = neopixel_colors[action_to_do]
        np.write()
    elif action_to_do == config.LED_CYCLE:
        cycle_colors();

#_thread.start_new_thread(cycle_colors, ())

from SimpleHttp import SimpleHttpServer
shs = SimpleHttpServer(do_action)
shs.run()
#from mini_server import MinimalServer
#ms = MinimalServer
#ms.run()