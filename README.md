# MicroPython Projects

### A Personal History

Since 2020 I have been using MicroPython on a number of embedded devices. My
journey with MicroPython started with PyCom devices in 2020. The PyCom device
I worked with was the FiPy. The was built around the Espressif 32-bit dual core
LX6 processor, with 4 MB of memory and 8 MB of FLASH. It had many other features,
notably LoRa, Sigfox, WiFi, Bluetooth Low Energy (BLE), and cellular LTE–CAT M1/NB1.

Pycom shipped the FiPy with their forked version of MicroPython 1.11. They added
drivers for LoRa, Sigfox, and LTE, as well as MicroPython support for those
devices.

Using the FiPy and the PyTracker, I created a LoRa-based mesh networked portable
system written in MicroPython. The system was meant to track the position of 
people and vehicles, and to relay that information back to a central computer 
that then displayed all those positions on a map in near-real-time. 

Unfortunately the money that initially provided impetus for this project wasn't 
renewed, and it eventually landed in my lap. If you're curious about the 
software, it's in the folder TeamTrack2.

### What Followed Next

I wasn't particularly happy with Pycom's version of MicroPython. My biggest
issue with Pycom's version was how it would randomly core dump, causing the device
to restart. I tried to determine the cause and a fix, but support was not very
good.

In 2021 I began to notice that Espressif was releasing development boards using
the ESP32-S3. The ESP32-S3 had WiFi and BLE, and was based on the LX7 core. The
boards were sold with various mixes of RAM and FLASH amounts; I eventually settled
on N8R8 (8 MB FLASH, 8 MB RAM) and N32R8 (32 MB of FLASH, 8 MB of RAM). I also
downloaded and installed Espressif's ESP-IDF framework and started to program
the boards in C and C++. It was with release 4.x that I started using the ESP-IDF.

I also forked the MicroPython source repo. It was from my fork that I would clone
down to my development system (Linx Mint) and build my own MicroPython firmware,
which I then flashed onto the boards. I did this primarily to create a firewall
between developers checking into the MicroPython project and work I was doing
at the time. One of the side benefits of having my own copy is that I could
see all the changes that occured on the main project branch before syncing my
copy, and then syncing my github copy with my system copy.

I also had the benefit of having firmware with up-to-date fixes and being built
with Espressif's latest tools. It concerned me that the MicroPython project had
fallen behind its using up-to-date Espressif tooling.

The fundamental issue at the time was that MicroPython did not support a number
of advanced Espressif boards. I had to configure my copy to support the type
and amount of RAM and FLASH in order for MicroPython to work on the ESP32-S3
boards in my possession.

As of MicroPython 1.24.0, that is no longer an issue. You can download firmware
from the MicroPython website and it will boot and run properly.

### Naming Nomenclature

All of my devices use a naming nomencature that is synthesized from the board's
system name and the last four digits of the board's unique ID.
```python
import binascii
import os
UNAME = os.uname().sysname.upper()
UNIQUE_ID = binascii.hexlify(ma.unique_id()).decode('ascii').upper()
SSID = UNAME + '-' + UNIQUE_ID[-4:]
```
I call the final result _SSID_ because a number of the Espressif boards are
programmed to act as stand-alone WiFi access points. Whether the SSID is used
for that or not, it makes for a unique identifier for all the boards. 

### WARNING

There's a lot of duplicated code across all the devices. It all works, but
there are some devices with more 'correct' code than others.

## Espressif Device Listing

### These folders under Espressif

| Board                    | Version | ID           | Folder Name   | Feature | AD |
|--------------------------|---------|--------------|---------------|-----------------|--------|
|ESP32-S3-DevKitC-1.1-N32R8| 1.24.0  | ESP32S3-287C | ESP32S3-287C  | WiFi AP| |
|ESP32-S3-DevKitC-1.1-N32R8| 1.24.0  | ESP32S3-287C | ESP32S3-287C-2| WiFi AP| |
|ESP32-S3-DevKitC-1.1-N8R8 | 1.24.0  | ESP32S3-4EF0 | ESP32S3-4EF0  | WiFi AP| |
|ESP32-S3-DevKitC-1.1-N8R8 | 1.24.0  | ESP32S3-4EF0 | ESP32S3-4EF0-2| WiFi AP| |
|ESP32-S3-DevKitC-1.1-N8R8 | 1.24.0  | ESP32S3-5554 | ESP32S3-5554  | WiFi AP| |
|ESP32-S3-DevKitC-1.1-N8R8 | 1.24.0  | ESP32S3-5554 | ESP32S3-5554-2| WiFi AP| |
|ESP32-S3-DevKitC-1.1-N8R8 | 1.24.0  | ESP32S3-5F50 | ESP32S3-5F50  | WiFi AP| |
|ESP32-S3-DevKitC-1.1-N8R8 | 1.24.0  | ESP32S3-5F50 | ESP32S3-5F50-2| WiFi AP| |
|ESP32-S3-DevKitC-1.1-N32R8| 1.24.0  | ESP32S3-5888 | ESP32S3-5888  | WiFi AP| |
|ESP32-S3-DevKitC-1.1-N32R8| 1.24.0  | ESP32S3-7814 | ESP32S3-7814  | WiFi AP| Yes |
|ESP32-S3-DevKitC-1.1-N8R8 | 1.24.0  | ESP32S3-C534 | ESP32S3-C534  | MAX7219 | |
|ESP32-S3-DevKitC-1.1-N32R8| 1.24.0  | ESP32S3-E138 | ESP32S3-E138  | WiFi AP| |
|ESP32-S3-DevKitC-1.1-N32R8| 1.24.0  | ESP32S3-E1D0 | ESP32S3-E1D0  | WiFi AP| |
|ESP32-S3-DevKitC-1.1-N32R8| 1.24.0  | ESP32S3-F838 | ESP32S3-F838  | WiFi AP| |

_The Version column is the MicroPython version in use._

_The AD column means under active development at the moment._

## Raspberry Pi Pico / Pico 2 Device Listing

### These folders under RPi

| Board                    | Version | ID       | Folder Name | Feature | AD |
|--------------------------|---------|----------|-------------|-----------------|--------|
| Raspberry Pi Pico        | 1.24.0  | RP2-3238 | RP2-3238    | | |
| Raspberry Pi Pico W      | 1.24.0  | RP2-4535 | RP2-4535    | | |
| Raspberry Pi Pico        | 1.24.0  | RP2-5936 | RP2-5936    | | |
| Raspberry Pi Pico        | 1.24.0  | RP2-8721 | RP2-8721    | | |
| Raspberry Pi Pico W      | 1.24.0  | RP2-9633 | RP2-9633    | | |
| Raspberry Pi Pico 2      | 1.24.0  | RP2-EC93 | RP2-EC93    | Running RISC V Cores | Yes |

_The Version column is the MicroPython version in use._

_The AD column means under active development at the moment._


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