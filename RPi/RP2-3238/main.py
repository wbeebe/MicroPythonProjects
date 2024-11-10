import gc
import os
import platform
import binascii
import machine as ma
import time

time.sleep_ms(500)

print()

print(f" MEM FREE: {gc.mem_free():,} BYTES")
UNAME = os.uname().sysname.upper()
stat_vfs = os.statvfs('/')
print(f" FS TOTAL: {stat_vfs[0] * stat_vfs[2]:,} BYTES")
print(f" FS  FREE: {stat_vfs[0] * stat_vfs[3]:,} BYTES")
print(f" PLATFORM: {platform.platform()}")

UNIQUE_ID = binascii.hexlify(ma.unique_id()).decode('ascii').upper()
print(f"      UID: {UNIQUE_ID}")
SSID = UNAME + '-' + UNIQUE_ID[-4:]
print(f"     SSID: {SSID}")
print(f" CPU FREQ: {ma.freq():,} Hz")
#
# Scan I2C bus for devices
#
SDA_PIN = ma.Pin(8) # Blue wire
SCL_PIN = ma.Pin(9) # Yellow wire
I2C = ma.I2C(0, scl=SCL_PIN, sda=SDA_PIN, freq=250000)
print(f"      I2C: {I2C}")
i2c_scanned = I2C.scan()

if len(i2c_scanned) == 0:
    print("      I2C: No Devices Found")
else:
    print("      I2C: DEVICES FOUND:", [hex(device_address)
        for device_address in i2c_scanned])

    # Check if there is an SSD1306 display attached.
    #
    import SSD1306
    import framebuf

    if SSD1306.OLED_ADDR in i2c_scanned:
        print("      I2C: SSD1306 OLED")
        #
        # Create instance of SSD1306 class to control the
        # display. Initialize it by clearing everything.
        #
        display = SSD1306.SSD1306_I2C(I2C)
        display.fill(0)
        #
        # Create a graphic of the Raspberry Pi logo.
        # Display it twice, one logo for each RP2040 core,
        # similar to what the regular Raspberry Pi does on
        # initial boot.
        # I copied the bytearray for the logo from Raspberry
        # Pi itself:
        # https://github.com/raspberrypi/pico-micropython-examples/tree/master/i2c
        #
        buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7C\x3F\x00\x01\x86\x40\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00\x7e\xfc\x00\x00\x4c\x27\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c\x20\x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        raspberry_pi_logo = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)
        display.framebuf.blit(raspberry_pi_logo, 0, 33)
        display.framebuf.blit(raspberry_pi_logo, 33, 33)
        #
        # Display the official MicroPython logo
        #
        display.framebuf.fill_rect(0, 0, 32, 32, 1)
        display.framebuf.fill_rect(2, 2, 28, 28, 0)
        display.framebuf.vline(9, 8, 22, 1)
        display.framebuf.vline(16, 2, 22, 1)
        display.framebuf.vline(23, 8, 22, 1)
        display.framebuf.fill_rect(26, 24, 2, 4, 1)
        #
        # Print some identifying text with the graphics, such
        # as version and the identifying string of the
        # Raspberry Pi Pico.
        #
        display.text('MicroPython', 40, 0, 1)
        display.text('-'.join(platform.platform().split('-')[1:3]), 40, 12, 1)
        display.text(SSID, 40, 24, 1)
        display.show()

print()

try:
    import network
    import socket

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
    
    ssid = "g00gleeeyes"
    password = "51538688"
    wifi.connect(ssid, password)
    
    html = """
        <!DOCTYPE html>
        <html>
            <head> <title>Pico W</title> </head>
            <body>
                <p>%s</p>
            </body>
        </html>
        """
    
    max_wait = 10
    while max_wait > 0:
        if wifi.status() < 0 or wifi.status() => 3:
            break;
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
        
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    
    print('listening on', addr)
    
except:
    print("  NETWORK: NO WIFI ON DEVICE")

print()
