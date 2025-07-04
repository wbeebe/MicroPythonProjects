"""
    Copyright 2025 William H. Beebe, Jr.

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

import time

print("      Main: START")
print("       LED: COLORS")
import devices
devices.cycle_colors()

print(" 7 SEG LED: TESTS")
import seven_segment
seven_segment.turn_on_all_segments()
time.sleep(5)
seven_segment.turn_off_all_segments()

print("  JOYSTICK: ENABLE")
import joystick
joystick.enable_center_button();

print("      Main: END")
from webserver import WebServer
web = WebServer(SSID, DISPLAY)
web.run()
