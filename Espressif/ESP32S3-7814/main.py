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

import machine  as ma
import neopixel as neo
import time     as ti
import config
import devices
import seven_segment

devices.cycle_colors()
seven_segment.test_segments()
seven_segment.test_numbers()

from webserver import WebServer
web = WebServer(SSID, DISPLAY)
web.run()
