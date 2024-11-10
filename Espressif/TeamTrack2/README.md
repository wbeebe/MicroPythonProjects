# TeamTrack
###### Last Update October 2023
## Software
### Firmware
All Pycom devices ship with Pycom device firmware v1.20.2.r4 installed on the FiPy. V1.20.2.r4 was released 12 January 2021. That release includes MicroPython v1.11, which is the language in which all of TeamTrack is written in. MicroPython 1.11 was released 29 May 2019.
- Pycom GitHub Firmware: https://github.com/pycom/pycom-micropython-sigfox/releases
- MicroPython GitHub: https://github.com/micropython/micropython/releases

## TeamTrack

TeamTrack stands for Team Tracking.

Functionality follows the major subsystems of the hardware, such as Bluetooth, WiFi (Web Server), LoRa, GPS, and Messaging.

TeamTrack WiFi is using Micro Web Server 2 (https://github.com/jczic/MicroWebSrv2).

Bluetooth functionality is disabled. With the Espressif ESP32 chip used in the FyPy, you can use WiFi or Bluetooth, but not both at the same time.

#### main.py
This is the first file to be executed on startup. All submodules (as classes) are instantiated, enabling hardware functionality. The end of main.py starts a series of threads for each major subsystem. Here a a number of the important threads.

The threaded function is `query_real_time_clock(delay)`, for many timed TeamTrack functions.
- Query the real time clock (across I2C)
- Read the battery power level
- Read SoC internal temperature and current running frequency
- Build up text for the OLED display and send it to the OLED display (across I2C)
- Communicate with the attached intelligent device(s) (OLED display, another SoC such as a Feather M0, across I2C)
    - The GPS and RTC are also on the I2C buss, but Pycom libraries are used to communicate with them.

The threaded function `show_visual_health()` flashes the on-board FiPy NeoPixel various colors depending on internal state. This is primarily for development.

The threaded function `query_position(delay)` queries the Pytrack V2 GPS radio for position and will set the internal Real Time Clock (RTC) from the UTC time contained in GPS messages.

#### config.py
This file contains many configurable constants and system-wide definitions. Each configurable constant has a comment block that explains what it will do in main.py and other modules.

#### gps.py
A wrapper class that reads the Pytrack V2 board's GPS module. It will also set the real-time clock from the GPS time when GPS is acquired. The RTC time, like GPS time, is UTC.

#### json.py
A class to implement JSON functionality. The class converts CSV to JSON and JSON to CSV. The class method that converts to JSON sits between websocket input the LoRa command processor and the class method that converts to CSV sits between the logging function and the websocket output for JSON.

#### lora.py
Wrapper class for using the LoRa radio. This class uses "raw" LoRa. All messages are sent and recieved by this class. The class exposes a method to convert CSV commands into internal LoRa binary messages. The class manages mesh networking.

#### messages.py
All the message type definitions.

#### oled.py
A wrapper class for managing and writing to the OLED display.

#### MicroWebSrv2
Folder containing the entire MicroWebSrv2 package. The web server is instantiated in main.py. All the HTTP routes are defined in main.py. The regular websocket (/wsheartbeat) used to route out messages such at all the various heartbeat messages in CSV format is defined in main.py. The JSON websocket (/wsjson) used to route out messages in JSON format is defined in main.py.

#### www
Folder containining all HTML, CSS, and JavaScript files used by the MicroWebSrv2 package.

#### lib
Folder containing all Pycom provided libraries to aid in using the underlying hardware.

## End Notes
### Bluetooth Functionality
Bluetooth functionality has been turned off. There is a flag named ENABLE_BLUETOOTH in config.py that enables Bluetooth functionality. It is currently set to False. Unless for development, do not enable until further notice.

When Bluetooth is enabled, see [BluetoothTesting.md](BluetoothTesting.md) for testing details.

### Logging
[LOGGING.md](LOGGING.md) is available to describe logging.

### REPL
The code is threaded and leaves the REPL console available. Hitting return at any time will produced the REPL prompt, '>>>'. The problem is that the software is constantly emitting log messages that can interrupt typing, making use of the REPL while the code is executing nearly impossible. To use the REPL, hit a return, then [Control] F in the console. This will stop code execution.

### Using Git
These are notes for how to work within this repo's branch on a macOS host.

* Changing the Git password on macOS host. You'll run into this when you're forced to change your corporate login password.
```
git config --global credential.helper osxkeychain
```
When git is run again, it will ask for your username and new password.

* You're working on a branch in the repo and you need to push your local work up to an external repo. You have everything added and committed locally.
  - In this example I'm pushing everthing up to the repo branch:
```
git push origin branch_name:branch_name
```
  - When you need to push a tag and the tag is already in your local repo:
```
git push origin branch_name:branch_name tag v1.0.1
```
