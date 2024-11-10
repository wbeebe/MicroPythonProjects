import machine  as ma
import neopixel as neo
import time     as ti
import config
import os

name = os.uname().machine.split(' ')[-1]
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
    if action_to_do == config.LED_RED or action_to_do == config.LED_GREEN or action_to_do == config.LED_BLUE or action_to_do == config.LED_OFF:
        np[0] = neopixel_colors[action_to_do]
        np.write()
    elif action_to_do == config.LED_CYCLE:
        cycle_colors();

from SimpleHttp import SimpleHttpServer
shs = SimpleHttpServer(SSID, SOFT_I2C, do_action, PLATFORM)
shs.run()
