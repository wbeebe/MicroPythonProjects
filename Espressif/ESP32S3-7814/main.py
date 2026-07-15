"""
Copyright 2025, 2026 William H. Beebe, Jr.

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

import devices
import joystick
import seven_segment
from webserver import WebServer

print("      Main: START")
print("       LED: COLORS")
devices.cycle_colors()

print(" 7 SEG LED: TESTS")
seven_segment.test_segments()
seven_segment.test_numbers()
# seven_segment.turn_on_all_segments()
# time.sleep(5)
# seven_segment.turn_off_all_segments()

print("  JOYSTICK: ENABLE")
joystick.enable_center_button()
print("      Main: END")
web = WebServer(SSID, DISPLAY)
web.run()
