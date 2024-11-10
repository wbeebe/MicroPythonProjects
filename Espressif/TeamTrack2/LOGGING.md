# Logging
###### Last Update August 2022
## General

The Pytrack board has a built-in microSDHC card adapter. Testing has shown that MicroPython will work with microSDHC cards up to 32GB, formatted as FAT32. MicroPython will also support FAT16, but no other formats. Do not try a card larger than 32GB, or logging to the card will fail.

A single text log file is written to the root of the device. No other files are written to the device.

The name of the file on the microSDHC card is [NODE_NAME].TXT, where NODE_NAME is the unique name created by the TeamTrack software. The NODE_NAME consists of TT######, where ###### corresponds to the last six hexadecimal digits of the FiPy's unique numerical ID.

For example, if a card has the unique ID of 2462ABB554E4,
then the log file name would be TTB5554E.TXT.

It is always opened in append mode, meaning it will accumulate logging text over time. Because the cards have a FAT32 format, they can be managed with any computer that can at least read that format, which includes Windows, macOS, and any contemporary Linux distribution.

It is best to use a computer that can also write to and format that card. While the logging to the card is parsimonious, even with 32GB of storage the card will eventually fill up if left unchecked. The card can be emptied by deleting the lone log file, or the card can be fully formatted. For macOS there are two methods to reformat, one using the Disk Utility GUI, and one from the command line.

The GUI method on macOS using Disk Utility:
- Insert the micro SDHC card into a port
- macOS will recognize the card and show its icon on the desktop
- Launch Disk Utility
- Select the micro SDHC card from the list on the left
- Select Erase at the top of Disk Utility
- Type in a name for the drive if needed, then select a format in the dropdown
  - Make sure to select ExFat
- Select Erase
- Once complete, select Done

This is the example command line (shell) sequence for macOS:
```
diskutil eraseDisk FAT32 TTrk MBRFormat disk4
```
disk4 is used in this example because that is the name discovered when 'diskutil list' is executed at the command line.


### Example Logging

```
********** SYSTEM RESTART **********
Reset Reason:        POWERON RESET
TeamTrack Version:   #.#.#
Unique ID:           F008D1CBCF4C
Machine:             FiPy with ESP32
Firmware Release:    1.20.2.r4
MicroPython Version: v1.11-ffb0e1c on 2021-01-12
LoRaWan Version:     1.0.2
SigFox Version:      1.0.1
Pybytes Version:     1.6.1
LORA MACADDR:        70b3d54992efa8c
WiFi SSID:           LTCBCF4C
IP ADDRESS:          192.168.1.2
...
```
The start of a logging session corresponds to the reset of the device. The start will always lead off with SYSTEM RESTART. What follows from there is device information.
* Reset Reason: Why the system was reset/restarted.
* TeamTrack Version: Software version of TeamTrack code.
* Unique ID: The FiPy's WiFi MAC address.
* Machine: Device's product name and type of microprocessor.
* Firmware Release: Pycom internal firmware version running on this FiPy.
* MicroPython Version: The version of MicroPython running on this device, and he date of its last update.
* LoRaWan Version: Version of LoRaWan software running on this device.
* SigFox Version: Version of SigFox software running on this device.
* Pybytes Version: Version of Pybytes software running on this device.
* LORA MACADDR: LoRa machine address, again unique.
* WiFi SSID: Derived from the machine ID. The last six digits of he unique ID are appended to LT to create a unique name.
* IP ADDRESS: The standard 192.168.1.2 address for all nodes.

After the startup information block, there will appear one or more repeating log statements. What follows is a sample of current logging:
```
...
SCAN I2C DEVICES
   OLED: FOUND DEVICE @ 0x3d
Pycom MicroPython 1.20.2.r4 [v1.11-ffb0e1c] on 2021-01-12; FiPy with ESP32
Pybytes Version: 1.6.1
Type "help()" for more information.
LED: SHOW_VISUAL_HEALTH
RTC: QUERY_REAL_TIME_CLOCK: START
LORA_SEND: SEND_LORA_HEARTBEAT: START
WEB: RUN WEB SERVER
Power,100%
WhoAmI,LTCBCF4C,1.0.1
Nodes,LTCBCF4C
GPS: START_QUERY_POSITION
Heartbeat,LTCBCF4C,NO_ALARM,100,-56
WLAN MODE: 2
WEB: LOAD WEB SOCKETS.
WEB: INSTANTIATE MICROWEBSRV2
WEB: START MICROWEBSRV2 MANAGED.
MWS2-INFO> Server listening on 0.0.0.0:80.
MWS2-INFO> Starts the managed pool to wait for I/O events.
GPS: RTC sync attempt to GPS time
GPS: RTC sync to GPS successful
...
```
* RTC: Real Time Clock. The format is YYYY/M/D-HH:MM:SS. Written to the log file every 60 seconds.
* PWR: shows the power situation. If USB, then USB is plugged in and all power coming from USB. If a percentage starting at 100%, then on the internal battery. As a sanity check the voltage measured is also logged.
* GPS: Writes out latitude and longitude. If there is no GPS reception, then logs nothing.
* WEB: A series of status messages showing how the Web Server starts up.
* Websocket: Indicates that the websocket has been successfully accessed and joined.

### Example LoRa Message Logging
```
...
MCU,160,61
Heartbeat,LTCBC578,NO_ALARM,100,-17,28.47347,-81.49711,2022/08/25-13:54:57_UTC
HeartBeat,LTCBC578,NO_ALARM,100,-17,28.47347,-81.49711,2022/08/25-13:54:57_UTC
Heartbeat,LT7B82BC,NO_ALARM,100,-25,28.473816,-81.497221,2022/08/25-13:55:25_UTC
Power,100%
WhoAmI,LT7B82BC,1.2.0
Nodes,LT7B82BC,LTB54C54,LTCBC578,LTCCBF54
Heartbeat,LTCCBF54,NO_ALARM,100,-9,28.47351,-81.49714,2022/08/25-13:55:12_UTC
Heartbeat,LTB54C54,NO_ALARM,100,-17,28.47347,-81.4972,2022/08/25-13:55:13_UTC
Heartbeat,LTCBC578,NO_ALARM,100,-28,28.47347,-81.49711,2022/08/25-13:55:03_UTC
HeartBeat,LTCBC578,NO_ALARM,100,-28,28.47347,-81.49711,2022/08/25-13:55:03_UTC
Heartbeat,LT7B82BC,NO_ALARM,100,-26,28.473816,-81.497221,2022/08/25-13:55:36_UTC
Heartbeat,LTCCBF54,NO_ALARM,100,-9,28.47351,-81.49714,2022/08/25-13:55:18_UTC
Heartbeat,LTB54C54,NO_ALARM,100,-19,28.47347,-81.49718,2022/08/25-13:55:23_UTC
Heartbeat,LT7B82BC,NO_ALARM,100,-24,28.473816,-81.497221,2022/08/25-13:55:42_UTC
Heartbeat,LTCCBF54,NO_ALARM,100,-17,28.47351,-81.49714,2022/08/25-13:55:24_UTC
Heartbeat,LTCBC578,NO_ALARM,100,-28,28.47347,-81.49711,2022/08/25-13:55:13_UTC
HeartBeat,LTCBC578,NO_ALARM,100,-28,28.47347,-81.49711,2022/08/25-13:55:13_UTC
Heartbeat,LTB54C54,NO_ALARM,100,-18,28.47347,-81.49718,2022/08/25-13:55:28_UTC
Heartbeat,LT7B82BC,NO_ALARM,100,-28,28.473816,-81.497221,2022/08/25-13:55:49_UTC
Heartbeat,LTB54C54,NO_ALARM,100,-17,28.47354,-81.49714,2022/08/25-13:55:35_UTC
Heartbeat,LTCBC578,NO_ALARM,100,-29,28.47347,-81.49711,2022/08/25-13:55:23_UTC
...
```
In its current implementation the code enables the underlying LoRa radio and then spins out a thread that is transmitting data. A callback is registered to receive data in an asynchronous manner.

* MCU: SoC operating frequency in MHz followed by temperature in degrees Centigrade.
* Power: Battery capacity from 0 to 100 percent.
* WhoAmI: Node unique ID followed by the version of TeamTrack software.
* Nodes: List of all nodes known by this node, includes this node in list
* Heartbeat: Message sent by this node as well as received from other nodes.
  - First field is message identifier Heartbeat
  - Second field is unique ID of node that sent the message
  - Third field is enumeration of health status
  - Forth field is battery capacity in percent
  - Fifth field is LoRa RSSI of last received message in dBm
  - Sixth field is latitude in decimal degrees
  - Seventh field is longitude in decimal degrees
  - Eight field is timestamp when message sent in UTM

### End Notes

Note that at this time there is no way for the correct time to be set in the RTC, thus the RTC always starts at midnight on 1 January 1970. Regardless, the RTC 60 second write is a way to determine the length of time between events with a resolution of one minute.

If the board can acquire a GPS fix, then the RTC will be set by the UTM time provided by GPS.
