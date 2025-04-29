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

from machine import Pin
import time as ti

# LED 7 segment display layout
# Part No. 5611 AH Common Cathode
#
#           Pin 7
#        ---- A ----
#        |         |
#  Pin 9 F         B Pin 6
#        |  Pin 10 |
#        ---- G ----
#        |         |
#  Pin 1 E         C Pin 4
#        |  Pin 2  |
#        ---- D ---- DP Pin 5
#                               ESP-32    5611 AH
A_SEGMENT = Pin(13, Pin.OUT)  # pin 19 to pin 7 *
B_SEGMENT = Pin(14, Pin.OUT)  # pin 20 to pin 6 *
F_SEGMENT = Pin(12, Pin.OUT)  # pin 18 to pin 9 *
G_SEGMENT = Pin(11, Pin.OUT)  # pin 17 to pin 10 *

E_SEGMENT = Pin(10, Pin.OUT)  # pin 16 to pin 1 *
D_SEGMENT = Pin( 9, Pin.OUT)  # pin 15 to pin 2 *
C_SEGMENT = Pin(16, Pin.OUT)  # pin  9 to pin 4 *
DP_SEGMENT = Pin(15, Pin.OUT) # pin  8 to pin 5 *

SEGMENTS = [
    A_SEGMENT,
    B_SEGMENT,
    C_SEGMENT,
    D_SEGMENT,
    E_SEGMENT,
    F_SEGMENT,
    G_SEGMENT,
    DP_SEGMENT,
    ]

DIGITS = [
    [0,0,0,0,0,0,0], # 0
    [0,1,1,0,0,0,0], # 1
    [1,1,0,1,1,0,1], # 2
    [1,1,1,1,0,0,1], # 3
    [0,1,1,0,0,1,1], # 4
    [1,0,1,1,0,1,1], # 5
    [1,0,1,1,1,1,1], # 6
    [1,1,1,0,0,0,0], # 7
    [1,1,1,1,1,1,1], # 8
    [1,1,1,0,0,1,1], # 9
    [1,1,1,0,1,1,1], # A
    [0,0,1,1,1,1,1], # b
    [1,0,0,1,1,1,0], # C
    [0,1,1,1,1,0,1], # d
    [1,0,0,1,1,1,1], # E
    [1,0,0,0,1,1,1], # F
    ]

def turn_off_all_segments():
    for segment in SEGMENTS:
        segment.off()

def test_segments():
    turn_off_all_segments()
    for segment in SEGMENTS:
        segment.on()
        ti.sleep_ms(500)
    turn_off_all_segments()

def print(digit):
    if digit > 15:
        return
    for i in range(len(DIGITS[digit])):
        SEGMENTS[i].value(DIGITS[digit][i])

def test_numbers():
    for i in range(16):
        print(i)
        ti.sleep_ms(500)

    ti.sleep_ms(1000)
    turn_off_all_segments()
