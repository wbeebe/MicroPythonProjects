import network
import ntptime
import socket
import machine as ma
import platform
import time
import settings
import webpage
import display_tools

def run(SSID, display, led):
    wifi = network.WLAN(network.STA_IF)
    network.hostname(SSID)
    wifi.active(True)
    wifi.connect(settings.AP_SSID, settings.AP_PWRD)

    while wifi.isconnected() == False:
        time.sleep_ms(1000)

    attempts = 10
    while attempts > 0:
        try:
            ntptime.settime()
            attempts = 0
            print(f"     WIFI: NTP Successful")
            print(f"      NTP: {webpage.formatted_time()}")
        except Exception as te:
            print(te)
            print(f"     WIFI: NTP {attempts}")
            time.sleep_ms(1000)
            attempts -= 1

    ip = wifi.ifconfig()[0]
    print(f"     WIFI: {ip}")
    display.text(str(ip), 0, 36, 1)
    display.show()

    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(4)

    print(f"     WIFI: Ready {ip}")

    while True:
        client = connection.accept()[0]
        request = str(client.recv(2048))
        #print(request)
        if 'LED+OFF=OFF' in request:
            led.value(0)
        if 'LED+ON=ON' in request:
            led.value(1)
        if 'DISPLAY+ON=ON' in request:
            display_tools.do_graphics(display, platform.platform(), SSID)
            display.text(str(ip), 0, 36, 1)
            display.show()
        if 'DISPLAY+OFF=OFF' in request:
            display.fill(0)
            display.show()

        client.send(webpage.webpage(SSID))
        client.close()
