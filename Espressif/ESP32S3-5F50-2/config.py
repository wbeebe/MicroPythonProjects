"""
   This code is licensed under Apache Apache Version 2.0, January 2004

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
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