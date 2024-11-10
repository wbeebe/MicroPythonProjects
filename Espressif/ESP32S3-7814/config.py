"""
   This code is licensed under Apache Apache Version 2.0, January 2004

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
"""
from micropython import const
import platform
import os

version_name = ' '.join(platform.platform().split('-')[0:2])
compiler="UNKNOWN"
for item in platform.platform().split('-'):
    if "IDF" in item:
        compiler = item
if compiler is "UNKNOWN":
    compiler = platform.python_compiler()
build_date = os.uname().version.split(' ')[-1]