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
from micropython import const

# Enumerations to perform a task.
LED_RED = const(0)
LED_GREEN = const(1)
LED_BLUE = const(2)
LED_OFF = const(5)
LED_CYCLE = const(6)

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
