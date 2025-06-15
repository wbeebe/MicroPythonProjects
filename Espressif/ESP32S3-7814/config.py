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

import platform
import os

if "preview" in platform.platform():
    version_name = ' '.join(platform.platform().split('-')[0:3])
else:
    version_name = ' '.join(platform.platform().split('-')[0:2])
compiler="UNKNOWN"
for item in platform.platform().split('-'):
    if "IDF" in item:
        compiler = item
if compiler is "UNKNOWN":
    compiler = platform.python_compiler()
build_date = os.uname().version.split(' ')[-1]