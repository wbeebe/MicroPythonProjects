import machine as ma
import neopixel as neo
import time as ti
from micropython import const

LED_RED = (32, 0, 0)
LED_GREEN = (0, 32, 0)
LED_BLUE = (0, 0, 32)
LED_CYAN = (0, 32, 32)
LED_MAGENTA = (32, 0, 32)
LED_YELLOW = (32, 16, 0)
LED_OFF = (0, 0, 0)

neopixel_colors = [
    LED_RED,
    LED_GREEN,
    LED_BLUE,
    LED_CYAN,
    LED_MAGENTA,
    LED_YELLOW,
    LED_OFF
    ]

pinnum = const(48)
np = neo.NeoPixel(ma.Pin(pinnum), 1)

def cycle_colors():
    for color in neopixel_colors:
        np[0] = color
        np.write()
        ti.sleep_ms(400)

def set_led_color(color):
    np[0] = color
    np.write()

# I2C pins for ESP32-S3-DevKit1
SDA_PIN = const(1)
SCL_PIN = const(2)

# SSD1306 OLED display
OLED_WIDTH = const(128)
OLED_HEIGHT = const(64)
OLED_LINE_MAX = const(6)
OLED_ADDR = const(61)

# ST25DV16K I2C RFID EEPROM
ST25DV_CMD = const(45)
ST25DV_USER_MEM = const(83)
ST25DV_SYS_MEM = const(87)
