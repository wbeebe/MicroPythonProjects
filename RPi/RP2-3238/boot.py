print()

import gc
print(f" MEM FREE: {gc.mem_free():,} BYTES")

import os
UNAME = os.uname().sysname.upper()
stat_vfs = os.statvfs('/')
print(f" FS TOTAL: {stat_vfs[0] * stat_vfs[2]:,} BYTES")
print(f" FS  FREE: {stat_vfs[0] * stat_vfs[3]:,} BYTES")

import platform
print(f" PLATFORM: {platform.platform()}")

import binascii
import machine as ma
UNIQUE_ID = binascii.hexlify(ma.unique_id()).decode('ascii').upper()
print(f"      UID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(f"     SSID: {SSID}")
print(f" CPU FREQ: {ma.freq():,} Hz")

# Scan I2C bus for devices
#
# I2C pins for Raspberry Pi Pico W, device I2C1
SDA_PIN = 26
SCL_PIN = 27
SOFT_I2C = ma.SoftI2C(scl=ma.Pin(SCL_PIN), sda=ma.Pin(SDA_PIN))
print(f"      I2C: {SOFT_I2C}")
i2c_scanned = SOFT_I2C.scan()

if len(i2c_scanned) == 0:
    print("      I2C: No Devices Found")
else:
    print("      I2C: DEVICES FOUND:", [hex(device_address)
        for device_address in i2c_scanned])

    # Display the Micropython logo on the SSD1306 OLED display.
    #
    import SSD1306

    if SSD1306.OLED_ADDR in i2c_scanned:
        display = SSD1306.SSD1306_I2C(SOFT_I2C)
        display.fill(0)
        display.framebuf.fill_rect(0, 0, 32, 32, 1)
        display.framebuf.fill_rect(2, 2, 28, 28, 0)
        display.framebuf.vline(9, 8, 22, 1)
        display.framebuf.vline(16, 2, 22, 1)
        display.framebuf.vline(23, 8, 22, 1)
        display.framebuf.fill_rect(26, 24, 2, 4, 1)
        display.text('MicroPython', 40, 0, 1)
        display.text('-'.join(platform.platform().split('-')[1:3]), 40, 12, 1)
        display.text(SSID, 40, 24, 1)
        display.show()

print()

try:
    import network
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    access_points = wifi.scan()
    networks = {}

    for network in access_points:
        if len(network[0]) > 0 and bytearray(network[0])[0] != 0:
            ssid = network[0].decode('utf-8')
            networks[ssid] = network[3]

    for ssid in sorted(networks.keys()):
        print(f"ssid: {ssid:24} rssi: {networks[ssid]}")
except ImportError:
    print("  NETWORK: NO WIFI ON PICO")

print()
