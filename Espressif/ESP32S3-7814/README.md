# ESP32S3-7814
## Major Changes

The ESP32-S3 developer board still executes MicroPython, in this case the latest pre-release.

| Board                    | Version | ID           | Folder Name   | Feature | AD  |
|--------------------------|---------|--------------|---------------|---------|-----|
|ESP32-S3-DevKitC-1.1-N32R8| 1.25.0  | ESP32S3-7814 | ESP32S3-7814  | MQTT    | Yes |

ESP32S3-7814 is no longer a stand-alone WiFi access point. Because of the addition of MQTT functionality, it now needs to connect to an external WiFi AP, such as a home WiFi access point. That external WiFi AP then allows it to connect to an MQTT broker.

This is the web page a fully functioning ESP32-S3 developer board presents now.

![Example webpage](../Assets/ESP32-S3-7814-Screenshot_20250614.png)

The view the web page presents is dynamic. Here's what that means:
1. If the OLED display isn't present, then the `Toggle OLED` button is not shown.
2. If the ESP32-S3 fails to connect with the MQTT broker then the `MQTT5 Test` button is not shown.
3. If the ESP32-S3 developer board does not a configured `vfs2` FLASH section, then the text at the bottom showing `vfs2 size` is not shown.

## Startup Output
This startup output is captured from Thonny's REPL window.
```
      Boot: START
    Memory: 8,307,008 bytes
     Flash: 33,554,432 bytes
  Platform: MicroPython 1.25.0 xtensa IDFv5.2.2 with newlib4.3.0
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
      MQTT: Subscribe to topic b'esp32-mqtt5/test'
      MQTT: Init ping timer: Timer(3, mode=PERIODIC, period=60000)
      MQTT: Broker connection successful to 192.168.0.210
```
## Development Environment
### Initial Setup
The following items and actions are required:
1. A home WiFi access point
2. A Raspberry Pi 5 8 GiB with Ubuntu 25.04 installed and connected to the home WiFi access point
3. Eclipse Mosquitto MQTT Broker (https://mosquitto.org) installed and running on the Raspberry Pi
4. ESP32-S3 with at least the latest MicroPython release flashed to the device
5. All the MicroPython files must be copied to an ESP32-S3.
### Application Software/Firmware Installation and Execution
#### MicroPython Firmware and Application
Install the latest MicroPython release to the ESP32-S3 development board. It can be found at [ESP32_GENERIC_S3](https://micropython.org/download/ESP32_GENERIC_S3/). Make sure to select from the _**Firmware (Support for Octal-SPIRAM)**_ section at the bottom if you have a development board with 8 MiB of SPIRAM. Select the `.bin`, not the `.uf2` version of the firmware. The download page provides full installation instructions.

Once the firmware is operational on the ESP32-S3 developer board, then upload all the Python files, and only the Python files, to the developer board.

You will need to create `settings.py` file that contains the two lines:
1. `AP_SSID = "your-wifi-SSID"` and
2. `AP_PASSWORD = "your-wifi-password"`,

with the appropriate SSID and password for your local WiFi access point. These are used by the file `webserver.py`. Once created flash onto the ESP32-S3 developer board with the rest of the MicroPython files.

#### Mosquitto
Install Mosquitto via `apt`:
```bash
$ sudo apt install mosquitto mosquitto-clients -y
```
Once installed make sure that the Mosquitto broker is up and running:
```bash
$ systemctl status mosquitto
● mosquitto.service - Mosquitto MQTT Broker
     Loaded: loaded (/usr/lib/systemd/system/mosquitto.service; enabled; preset: enabled)
     Active: active (running) since Tue 2025-06-10 22:01:46 EDT; 4 days ago
 Invocation: 809467da2f104de387c6a49227c287b8
       Docs: man:mosquitto.conf(5)
             man:mosquitto(8)
   Main PID: 18660 (mosquitto)
      Tasks: 1 (limit: 9354)
        CPU: 1min 5.536s
     CGroup: /system.slice/mosquitto.service
             └─18660 /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf

Jun 10 22:01:46 pi05-01 systemd[1]: Starting mosquitto.service - Mosquitto MQTT Broker...
Jun 10 22:01:46 pi05-01 mosquitto[18660]: 1749607306: Loading config file /etc/mosquitto/conf.d/default.conf
Jun 10 22:01:46 pi05-01 systemd[1]: Started mosquitto.service - Mosquitto MQTT Broker.
Jun 14 00:50:10 pi05-01 systemd[1]: Reloading mosquitto.service - Mosquitto MQTT Broker...
Jun 14 00:50:10 pi05-01 systemd[1]: Reloaded mosquitto.service - Mosquitto MQTT Broker.
```
In the example above Mosquitto is loaded and active (running). If it's not, then type `sudo systemctl start mosquitto` at the prompt and check the status again.
#### Development and Testing
Once the broker is up, open a terminal and type the following:
```bash
$ mosquitto_sub -i "esp32_mqtt5_tester" -t "esp32-mqtt5/test" -c &
```
Leave the terminal up. The `-i` switch is the subscriber identifier, and the `-t` switch is the topic, which must match the topic in the ESP32-S3 MicroPython code module `mqtt_tools.py`.

The application on the ESP32-S3 connects to the broker via the Mosquitto subscriber using topic `esp32-mqtt5/test`. Messages are sent from the ESP32-S3 in minified JSON and are echoed to the terminal.

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

## Changes and Updates
#### _16 June 2025_

A checkin to the MicroPython project has broken the build. I can't use that build and checkin on my ESP32-S3 developer board, so I've dropped back to the official 1.25.0 release. That is sufficient for my work, and what I'll stick with indefinately. This README has been updated to reflect this.