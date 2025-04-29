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

from micropython import const
#
# System configuration area
#
GPO      = const(0x00)
IT_TIME  = const(0x01)
EH_MODE  = const(0x02)
RF_MNGT  = const(0x03)
RFA1SS   = const(0x04)
ENDA1    = const(0x05)
RFA2SS   = const(0x06)
ENDA2    = const(0x07)
RFA3SS   = const(0x08)
ENDA3    = const(0x09)
RFA4SS   = const(0x0A)
MB_MODE  = const(0x0D)
MB_WDG   = const(0x0E)
LOCK_CFG = const(0x0F)
