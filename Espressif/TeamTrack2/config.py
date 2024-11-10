"""
System Wide Configuration Constants
"""
from network import LoRa
from micropython import const
import time

VERSION = "2.0"

# ----------------------------------------------------------------------------
# The ID_BASENAME and REG_STR are tied together; the ID name must be eight
# characters in length. Thus if the ID_BASENAME is 3 characters then then
# the REG_STR must be 5 characters. If the ID_BASENAME is changed then
# the REG_STR must subsequently be changed.
#
ID_BASENAME = "TT-"
#
# This is where Micro Python really falls down: regular expressions.
# In regular Python, you would use [\dA-F]{4} to match four consecutive
# hexadecimal numbers. Instead, I have to do the following ugly thing:
#
REG_STR = "[0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F]"
# ----------------------------------------------------------------------------
IPADDRESS = "192.168.1.2"
# ----------------------------------------------------------------------------
THREAD_STACK_SIZE = const(8192)
# ----------------------------------------------------------------------------
# Enable the BlueTooth module.
# If true, BlueTooth runs. If false, BlueTooth radios are off.
#
ENABLE_BLUETOOTH = False

# ----------------------------------------------------------------------------
# Period timeouts, or how long a thread will sleep, in seconds.
# Counters, or how many times to count before taking an action.
#
TIMER_GPS = const(5)
TIMER_RTC = const(2)
TIMER_BLUETOOTH = const(60)
TIMER_READ_BATTERY = const(30)

# ----------------------------------------------------------------------------
# LoRa critical configuration parameters
#
# LoRa channel bandwidth is in kHz, and can be 125, 250, or 500.
# It is configured in the LoRaTTrk constructor, using one of
# LoRa.BW_125KHZ (0), LoRa.BW_250KHZ (1), or LoRa.BW_500KHZ (2).The numeric
# values are enumerations defined in the MicroPython class.
#
def decode_lora_bw(bw):
    if bw == 0:
        return 'BW_125KHZ'
    elif bw == 1:
        return 'BW_250KHZ'
    elif bw == 2:
        return 'BW_500KHZ'
    return 'BW_UNKNOWN'

def decode_lora_power_mode(pm):
    if pm == 0:
        return 'ALWAYS_ON'
    elif pm == 1:
        return 'TX_ONLY'
    return 'PM_UNKNOWN'

def decode_lora_coding_rate(rate):
    if rate == LoRa.CODING_4_5:
        return 'CODING_4_5'
    elif rate == LoRa.CODING_4_6:
        return 'CODING_4_6'
    elif rate == LoRa.CODING_4_7:
        return 'CODING_4_7'
    elif rate == LoRa.CODING_4_8:
        return 'CODING_4_8'
    return 'CODING_UNKNOWN'
#
# LORA_MIN_TIMEOUT is in seconds.
# LORA_RND_TIMEOUT will add a random number of seconds
# to LORA_MIN_TIMEOUT. So, for example, if LORA_RND_TIMEOUT is 3, then
# the times between transmitting a heartbeat message will vary from
# LORA_MIN_TIMEOUT to LORA_MIN_TIMEOUT + 3 seconds.
#
LORA_MIN_TIMEOUT = const(15)
LORA_RND_TIMEOUT = const(5)
#
# After 30 TIMER_RTC tics (and thread runs), perform an action.
#
TIMER_RTC_COUNT = const(30)

# ----------------------------------------------------------------------------
# Check that GPS latitude and lonitude are within CONUS.
# This algorythm is hard coded just for the lower 48, as are the values.
#
# If the latitude and longitude are within the bounding region return true,
# else return false.
#
# Bounding box is bound box upper left (bbul) and bound box lower right (bblr).
#
bbul = [49.0, -124.0]
bblr = [24.0, -67.0]
def check_gps(lat, lon):
    if lat == None or lon == None:
        return False
    return bbul[0] >= lat and lat >= bblr[0] and bbul[1] <= lon and lon <= bblr[1]

# ----------------------------------------------------------------------------
# Colors to be used on the NeoPixel.
# The values set both color and output intensity.
#
BLACK = const(0x000000)
RED = const(0x200000)
GREEN = const(0x002000)
BLUE = const(0x000020)
VIOLET = const(0x200020)
YELLOW = const(0x201000)
WHITE = const(0x202020)

# ----------------------------------------------------------------------------
# Testing limits for the battery.
# These limits have been through observation of real-world batteries.
#
USB_NOMINAL = 4.0
BATTERY_MAX = 3.7
BATTERY_MIN = 3.3
PERCENTAGE_MAX = const(150)

# ----------------------------------------------------------------------------
# LoRa message constants and timeouts.
#
# How many consecutive internal heartbeats do I wait without recieving an
# external node's heartbeat before that external node is marked out-of-comms?
#
GROUP_COUNTDOWN = const(4)
OOCOMM_STOP = const(-2)

# ----------------------------------------------------------------------------
# Display constants.
#
MONO_OLED_128_64 = const(0x3D)     # I2C address
MONO_OLED_128_64_ROWS = const(64)  # in pixels
MONO_OLED_128_64_COLS = const(128) # in pixels

# ----------------------------------------------------------------------------
# Feather constants.
#
FEATHER_I2C = const(0x70)              # I2C address

# ----------------------------------------------------------------------------
# alarm_state constants
#
NO_ALARM = const(0)
ALARM = const(1)
CONFIRM_ALARM = const(2)
CLEAR_ALARM = const(3)

def decode_alarm_state(state):
    if state == 0:
        return 'NO ALARM'
    else:
        return 'ALARM {}'.format(state)

# ----------------------------------------------------------------------------
# Convert a time value into a formatted string:
#   year/month/day-hour:minute:seconds_UTC
#
# The returned string is UTC time.
#
def decode_datetime(datetime):
    ltime = time.localtime(datetime)
    return "{}/{:02}/{:02}-{:02}:{:02}:{:02}_UTC".format(
        ltime[0], ltime[1], ltime[2], ltime[3], ltime[4], ltime[5])
