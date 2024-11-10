from micropython import const

# Enumerations to perform a task.
LED_RED = const(0)
LED_GREEN = const(1)
LED_BLUE = const(2)
LED_CYCLE = const(3)
LED_OFF = const(5)

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
