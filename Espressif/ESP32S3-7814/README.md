# ESP32S3-7814

Rough notes. Unfinished, but what is currently here is accurate.

The ESP32-S3 developer board still executes MicroPython, in this case the latest pre-repease.

| Board                    | Version | ID           | Folder Name   | Feature | AD  |
|--------------------------|---------|--------------|---------------|---------|-----|
|ESP32-S3-DevKitC-1.1-N32R8| 1.26.0P | ESP32S3-7814 | ESP32S3-7814  | WiFi AP | Yes |
## Major Changes
ESP32S3-7814 is no longer a stand-alone WiFi access point. Because of the addition of MQTT functionality, it now needs to connect to an external WiFi AP. That external WiFi AP then allows it to connect to an MQTT broker.

This is what a fully functioning ESP32-S3 developer board presents now via its built-in web page.

![Example webpage](../Assets/ESP32-S3-7814-Screenshot_20250614.png)

The view the web page presents is dynamic. Here's what that means:
1. If the OLED display isn't present, then the `Toggle OLED` button is not shown.
2. If the ESP32-S3 fails to connect with the MQTT broker then the `MQTT5 Test` button is not shown.
3. If the ESP32-S3 developer board does not have 32 MiB of FLASH and if there is, as a consequence, no `vfs2` FLASH section, then the text at the bottom showing `vfs2 size` is not shown.

## Typical startup output (captured via Thonny console).
```
      Boot: START
    Memory: 8,307,008 bytes
     Flash: 33,554,432 bytes
  Platform: MicroPython 1.26.0 preview xtensa IDFv5.4.1 with newlib4.3.0
 Unique ID: 68B6B33D7814
      SSID: ESP32S3-7814
 CPU Clock: 160,000,000 Hz
       I2C: SoftI2C(scl=2, sda=1, freq=500000)
       I2C: Devices found: ['0x3d']
       I2C: SSD1306 OLED Found
      Boot: END
      Main: START
       LED: COLORS
 7 SEG LED: TESTS
  JOYSTICK: ENABLE
      Main: END
      WIFI: Connected
      WIFI: 192.168.0.174
      WIFI: NTP Connection Attempt #1
      WIFI: NTP Connection Successful
      DATE: 4:31 PM  Saturday 14 June 2025
      MQTT: Broker connection start from ESP32S3-7814 to 192.168.0.210
      MQTT: Set callback
      MQTT: Connect
      MQTT: Subscribe to topic b'boost-mqtt5/test'
      MQTT: Init ping timer: Timer(3, mode=PERIODIC, period=60000)
      MQTT: Broker connection successful to 192.168.0.210
```
## Basic MQTT Architecture
+ A home WiFi access point
+ A Raspberry Pi 5 8 GiB with Ubuntu 25.04 installed and connected to the home WiFi access point
+ Eclipse Mosquitto MQTT Broker (https://mosquitto.org) installed and running on the Raspberry Pi
+ ESP32-S3 with MicroPython 1.26 pre-release running umqtt.robust and connecting to the Mosquitto MQTT broker via the home WiFi access point

The application on the ESP32-S3 connects to the broker using topic `boost-mqtt5/test`. Messages are sent from the ESP32-S3 in minified JSON.

Example ESP32-S3 minified JSON messages:
```
 {"LED":"ESP32S3-7814","DATE":"9:12 PM  Saturday 14 June 2025","COLOR":"RED","STATE":"ON"}
 {"LED":"ESP32S3-7814","DATE":"9:12 PM  Saturday 14 June 2025","COLOR":"RED","STATE":"OFF"}
 {"LED":"ESP32S3-7814","DATE":"9:12 PM  Saturday 14 June 2025","COLOR":"GREEN","STATE":"ON"}
 {"LED":"ESP32S3-7814","DATE":"9:12 PM  Saturday 14 June 2025","COLOR":"GREEN","STATE":"OFF"}
 {"LED":"ESP32S3-7814","DATE":"9:12 PM  Saturday 14 June 2025","COLOR":"BLUE","STATE":"ON"}
 {"LED":"ESP32S3-7814","DATE":"9:12 PM  Saturday 14 June 2025","COLOR":"BLUE","STATE":"OFF"}
 {"TEST":"ESP32S3-7814","DATE":"9:12 PM  Saturday 14 June 2025","COMPILER":"IDFv5.4.1","BUILD_DATE":"2025-06-07"}
 {"PING":"ESP32S3-7814","DATE":"9:12 PM  Saturday 14 June 2025"}
```
LED messages are generated from the web page buttons toggling the color LED. Tells the current color and if it's on or off.

The PING message is sent every 60 seconds.