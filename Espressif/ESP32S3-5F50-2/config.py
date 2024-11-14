"""
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
"""
from micropython import const
import platform
import os

# Enumerations to perform a task.
#
LED_RED = const(0)
LED_GREEN = const(1)
LED_BLUE = const(2)
LED_CYCLE = const(3)
LED_OFF = const(5)

version_name = ' '.join(platform.platform().split('-')[0:3])
compiler = platform.platform().split('-')[4]
build_date = os.uname().version.split(' ')[-1]