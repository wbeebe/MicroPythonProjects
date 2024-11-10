"""
Main software for the TeamTrack stack.
Instantiate all the classes involved in the functionality of the
FiPy and PyTrack boards that make up the device.
"""
import machine
import binascii
import os
import pycom
import time
import _thread

import config
from json import JsonTTrk

# ----------------------------------------------------------------------------
# Turn off the FiPy's blinking blue LED.
#
pycom.heartbeat(False)
time.sleep(1)

# ----------------------------------------------------------------------------
# Set thread stack size here.
#
_thread.stack_size(config.THREAD_STACK_SIZE)

# ----------------------------------------------------------------------------
# Stringify the board's WiFi MACADDR, which corresponds to the board's
# unique ID. We'll use this not just for WiFi but where-ever we need a
# unique identifier.
#
UNIQUE_ID = binascii.hexlify(machine.unique_id()).decode('ascii').upper()

# ----------------------------------------------------------------------------
# Create a unique SSID from the last five digits of the hexadecimal unique ID.
#
SSID = config.ID_BASENAME + UNIQUE_ID[-5:]

# ----------------------------------------------------------------------------
# The LOG function determines if a properly formatted micro SDXC card
# has been inserted into the Pytrack.
# If one has then LOG writes to the card as well as the console output,
# otherwise it just prints to the console.
#
# NOTE: The largest usable SDXC card is 32GB formatted as FAT32.
# The SD class will only handle FAT16 and FAT32 filesystem cards.
#
logfile = None
logfileName = "/sd/{}.TXT".format(SSID)
from machine import SD

try:
    sd = SD()
    os.mount(sd, '/sd')
    logfile = open(logfileName, 'a')
    print(" ++++++++++ LOGFILE OPEN ++++++++++")
    print(" ++++++++++ {} ++++++++++".format(logfileName))
except:
    logfile = None

_webSocket = None
_webJsonSocket = None
_json = JsonTTrk(SSID)

def LOG(text_to_log, send_to_websocket = False):
    if text_to_log is None:
        return

    global logfile
    global _webSocket
    print(text_to_log)
    json_text = _json.convert_to_json(text_to_log)

    if logfile != None:
        logfile.write("{}\n".format(text_to_log))
        logfile.flush()

    if send_to_websocket and _webSocket != None:
        _webSocket.SendTextMessage(text_to_log)

    if send_to_websocket and _webJsonSocket != None and json_text != None:
        print(json_text)
        if logfile != None:
            logfile.write("{}\n".format(json_text))
            logfile.flush()
        _webJsonSocket.SendTextMessage(json_text)

LOG("\n ********** SYSTEM RESTART **********\n")

# ----------------------------------------------------------------------------
# Log what the reason was for restarting the FiPy
#
def get_reset_cause():
    rc = machine.reset_cause()
    if rc == machine.PWRON_RESET:
        return "POWERON RESET"
    elif rc == machine.HARD_RESET:
        return "HARD RESET"
    elif rc == machine.WDT_RESET:
        return "WATCHDOG TIMER RESET"
    elif rc == machine.DEEPSLEEP_RESET:
        return "DEEPSLEEP RESET"
    elif rc == machine.SOFT_RESET:
        return "SOFT RESET"
    elif rc == machine.BROWN_OUT_RESET:
        return "LOW VOLTAGE"
    else:
        return "UNKNOWN RESET REASON"

# ----------------------------------------------------------------------------
# Saved GPS coordinates to be used by multiple modules.
# We calculate just once and use everywhere else.
#
gcoords = (None, None)

def get_gcoords():
    global gcoords
    return gcoords

# ----------------------------------------------------------------------------
# Provide functions to return the status of the global alarm_state for other
# users, and to set it based on incoming LoRa messages.
#
alarm_state = config.NO_ALARM

def get_alarm_state():
    global alarm_state
    return alarm_state

def set_alarm_state(new_alarm_state):
    global alarm_state
    alarm_state = new_alarm_state
    LOG('SetAlarmState,{},{}'.format(
        SSID, config.decode_alarm_state(alarm_state)))

# ----------------------------------------------------------------------------
# Show the alarm_state state of the node through the color of the LED.
# This displays on the internal LED. This will only be seen if the electronics
# are visible as this LED is surface mounted on the FiPy board itself.
#
def show_alarm_state():
    global alarm_state
    LOG(' LED: SHOW_ALARM_STATE')
    while True:
        if alarm_state == config.NO_ALARM:
            led = config.GREEN
        elif alarm_state == config.ALARM:
            led = config.RED
        elif alarm_state == config.CONFIRM_ALARM:
            led = config.WHITE

        pycom.rgbled(led)
        time.sleep(1)
        pycom.rgbled(config.BLACK)
        time.sleep(1)

# ----------------------------------------------------------------------------
# GPS support.
#
from gps import GPS
from pytrack import Pytrack
from machine import RTC
rtc = RTC()

def query_position(delay):
    global rtc
    LOG(' GPS: START_QUERY_POSITION')
    py = Pytrack()
    gps = GPS(LOG, py, timeout=delay)
    global gcoords
    global i2c

    while True:
        done = False
        coord = None, None
        while not done:
            try:
                coord = gps.coordinates(debug=False)
            except OSError as ose:
                LOG('! I2C_OSError query_position {}'.format(ose.args))
                time.sleep_us(100)
                i2c.deinit()
                time.sleep_us(100)
                i2c.init(I2C.MASTER, baudrate=50000)

            if coord[0] != None:
                done = config.check_gps(coord[0], coord[1])
            else:
                done = True

        gcoords = coord

        if coord[0] != None:
            gps.set_rtc(rtc)

        time.sleep(delay)

# ----------------------------------------------------------------------------
# Check the battery and determine how much is left in percent.
#
adc_reading = 0
percentage_text = 'RESET'
percentage_value = 0

def read_battery(send_log):
    global adc_reading
    global percentage_text
    global percentage_value
    py = Pytrack()
    #
    # Round the battery voltage reading to one decimal place to avoid
    # percentages from bouncing around.
    #
    adc_reading = round(py.read_battery_voltage(),1)
    numerator = adc_reading - config.BATTERY_MIN
    denominator = config.BATTERY_MAX - config.BATTERY_MIN
    percentage_value = int((numerator / denominator) * 100)
    if percentage_value > 100:
        percentage_value = 100
    percentage_text = "{}%".format(percentage_value)
    if send_log:
        LOG("Power," + percentage_text, True)

def get_battery_percentage():
    global percentage_text
    return percentage_text

def get_battery_percentage_value():
    global percentage_value
    return percentage_value

# ----------------------------------------------------------------------------
# Read the MCU clock frequency and the MCU temperature. We need to keep an
# eye on the temperature in particular, as if the MCU gets too hot then it
# will self-throtle its frequency.
#
mcu_freq_and_temp_text = 'UNKNOWN'

def get_mcu_freq_and_temp():
    return mcu_freq_and_temp_text

def read_mcu_freq_and_temperature(send_log):
    global mcu_freq_and_temp_text
    mcu_freq = int(machine.freq()/1e+6)
    mcu_temp = (machine.temperature() - 32)/1.8
    mcu_freq_and_temp_text = "{}MHz {:.0F}C".format(mcu_freq, mcu_temp)
    if send_log:
        LOG("MCU,{},{:.0F}".format(mcu_freq, mcu_temp), True)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# I2C support functionality.
#
# Scan for I2C devices. Configure and enable any that are found.
#
from machine import I2C
from machine import Pin
from oled import Oled_I2C
oled_display = None
feather_dev = None
i2c = None

def find_i2c_devices():
    global oled_display
    global feather_dev
    global i2c
    LOG(' SCAN I2C DEVICES')
    i2c = I2C(0, mode=I2C.MASTER, baudrate=50000, pins=('P22', 'P21'))
    for i2c_dev in i2c.scan():
        if i2c_dev == config.MONO_OLED_128_64:
            LOG("    OLED: FOUND DEVICE @ 0x{:02x}".format(i2c_dev))
            oled_display = Oled_I2C(
                config.MONO_OLED_128_64_COLS,
                config.MONO_OLED_128_64_ROWS, i2c, i2c_dev)
            #oled_display.fill(0)
            #oled_display.text(SSID, 0, 0)
        elif i2c_dev == config.FEATHER_I2C:
            LOG(" FEATHER: FOUND DEVICE @ 0x{:02x}".format(i2c_dev))
            feather_dev = Feather(i2c, i2c_dev)

# ----------------------------------------------------------------------------
#
class Feather():
    global SSID
    global alarm_state
    global gcoords

    def __init__(self, i2c, i2c_dev):
        self.i2c = i2c
        self.i2c_dev = i2c_dev
        self.buf = bytearray(2)
        self.nameBuf = bytearray()
        self.nameBuf.append(0x30)
        self.nameBuf += bytearray(SSID, 'utf-8')
        self.nameBuf.append(0x7F)
        self.verBuf = bytearray()
        self.verBuf.append(0x31)
        self.verBuf += bytes(config.VERSION, 'utf-8')
        self.verBuf.append(0x7f)
        self.bigBuf = bytearray()
        self.bigBuf.append(0x30)
        self.bigBuf += bytearray(SSID, 'ascii')
        self.bigBuf += bytearray(config.VERSION, 'ascii')
        self.bigBuf.append(0x30 + alarm_state)
        self.bigBuf.append(0x30)
        self.bigBuf.append(0x7f)
        self.counter = 0

    def test(self):
        self.buf[0] = 0x80
        self.buf[1] = self.counter.to_bytes(1, 'little')[0]
        self.counter += 1
        try:
            self.i2c.writeto(self.i2c_dev, self.buf, stop=True)
        except OSError as ose:
            LOG('! I2C_OSError test {}'.format(ose.args))
            time.sleep_us(100)
            self.i2c.deinit()
            time.sleep_us(100)
            self.i2c.init(I2C.MASTER, baudrate=50000)

    def sendNodeState(self):
        try:
            self.bigBuf[16] = (0x30 + alarm_state)
            if gcoords[0] is not None:
                self.bigBuf[17] = 0x31
            else:
                self.bigBuf[17] = 0x30
            self.i2c.writeto(self.i2c_dev, bytes(self.bigBuf))
        except OSError as ose:
            LOG('! I2C_OSError sendNodeState {}'.format(ose.args))
            time.sleep_us(100)
            self.i2c.deinit()
            time.sleep_us(100)
            self.i2c.init(I2C.MASTER, baudrate=50000)

# ----------------------------------------------------------------------------
# Bluetooth functionality
#
if config.ENABLE_BLUETOOTH:
    from bluetooth import BluetoothTTrk
    bluetooth = BluetoothTTrk(SSID,LOG)

# ----------------------------------------------------------------------------
# LoRa functionality. Instantiating an instance of our LoRa Python class
# turns on the radio and enables all its functionality, especially
# sending and recieving messages.
#
from lora import LoRaTTrk
lora = LoRaTTrk(SSID, LOG,
    get_alarm_state, set_alarm_state, get_battery_percentage_value, get_gcoords)

# ----------------------------------------------------------------------------
# Running on a thread.
# Print/log the real-time clock.
# Print/log MCU frequency and temperature.
# If the OLED was found and configured then use this thread to update the OLED
# as well.
#
def query_real_time_clock(delay):
    global oled_display
    global feather_dev
    global percentage_text
    global alarm_state

    LOG(' RTC: QUERY_REAL_TIME_CLOCK: START')
    my_count = 0
    toggle = False
    ctoggle = '+'

    while True:
        # Log certain information every 60 seconds, and make certain
        # measurements every 60 seconds.
        #
        if my_count == 0:
            my_count = config.TIMER_RTC_COUNT
            LOG(lora.who_am_i(), True)
            LOG(lora.list_group_nodes(), True)
            read_mcu_freq_and_temperature(True)
            read_battery(True)
        else:
            my_count -= 1

        # Proof-of-life character changes every second.
        # If the character doesn't change then the system is truly locked up.
        #
        if toggle is True:
            ctoggle = '*'
            toggle = False
        else:
            ctoggle = '+'
            toggle = True

        # Refresh the OLED every two seconds, or config.TIMER_RTC seconds
        #
        if oled_display is not None:
            oled_display.fill(0)
            oled_display.text(SSID, 0, 0)
            alarm_state_text = config.decode_alarm_state(alarm_state)
            oled_display.text(alarm_state_text, 0, 10)
            snodes = 'NET' if lora.count_group_nodes() > 0 else '   '
            oled_display.text(snodes, 0, 30)
            # Text characters are 6x6, the cell is 7x8.
            # Multiply number of characters to start in a line by 7.
            #
            sgps = 'GPS' if gcoords[0] is not None else '   '
            oled_display.text(sgps + ctoggle, 35, 30)
            oled_display.text(percentage_text, 0, 50)
            oled_display.show()

        if feather_dev is not None:
            time.sleep_us(100)
            feather_dev.sendNodeState()
            #time.sleep_us(500)
            #feather_dev.sendVersion()

        time.sleep(delay)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
#
# Enable web server as an access point.
#
import usocket
from network import WLAN
from MicroWebSrv2 import *
import gc

gc.enable()

# ----------------------------------------------------------------------------

@WebRoute(GET, '/')
def MainTTrk(microWebSrv2, request):
    global SSID
    global gcoords
    mycoords = (0,0)
    if gcoords[0] != None:
        mycoords = gcoords
    stime = config.decode_datetime(time.time())

    content = """\
    <!DOCTYPE html>
    <html>
        <head>
            <title>TeamTrack Control Panel</title>
            <link rel="stylesheet" href="ttrk.css" />
        </head>
        <body>
            <h1>TeamTrack Node {}</h1>
            <hr/>
            <div class="flex-container">
                <a href='/dashboard.html'><button class='green_button'>CSV Dashboard</button></a>
                <a href='/dashboard_json.html'><button class='green_button'>JSON Dashboard</button></a>
                <a href='/lorastats'><button class='green_button'>LoRa Statistics</button></a>
                <a href='/about'><button class='green_button'>About</button></a>
            </div>
            <hr/>
            <div class="flex-container">
                <h2><div class="internals">&nbsp;Latitude: {:.6f}</div><br/>
                <div class="internals">Longitude: {:.6f}</div><br/>
                <div class="internals">Time: {}</div></h2>
            </div>
            </body>
        </body>
    </html>
    """.format(SSID, mycoords[0], mycoords[1], stime)
    request.Response.ReturnOk(content)

# ----------------------------------------------------------------------------

def make_human_readable(value):
    if value < 1000:
        return '{} B'.format(value)
    kvalue = value/1024
    if kvalue < 1000:
        return '{:0.1f} KiB'.format(kvalue)
    mvalue = kvalue/1024
    return '{:0.1f} MiB'.format(mvalue)

# ----------------------------------------------------------------------------

@WebRoute(GET, '/about')
def AboutTTrk(microWebSrv2, request):
    global gcoords
    global percentage_text
    _uname = os.uname()
    logsizetext = 'None'
    if logfile != None:
        logsizetext = make_human_readable(os.stat(logfileName)[6])
    content = """\
    <html>
    <head>
        <title>About TeamTrack Mesh</title>
        <link rel="stylesheet" href="ttrk.css" />
    </head>
    <body>
        <h1>About Node {}</h1>
        <hr/>

        <table>
        <tbody>
        <tr><td>TeamTrack</td><td>V{}</td></tr>
        <tr><td>Unique ID</td><td>{}</td></tr>
        <tr><td>Pycom Product</td><td>{}</td></tr>
        <tr><td>Firmware Release</td><td>{}</td></tr>
        <tr><td>MicroPython Version</td><td>{}</td></tr>
        <tr><td>LoRaWan Version</td><td>{}</td></tr>
        <tr><td>SigFox Version</td><td>{}</td></tr>
        <tr><td>Pybytes Version</td><td>{}</td></tr>
        <tr><td>LoRa MACADDR</td><td>{}</td></tr>
        <tr><td>Power</td><td>{}</td></tr>
        <tr><td>Internal</td><td>{}</td></tr>
        <tr><td>Memory free</td><td>{}</td></tr>
        <tr><td>Log File</td><td>{}</td></tr>
        </tbody>
        </table>

        <hr/>
        <div class="flex-container">
            <a href='/'><button class='green_button'>Return</button></a>
        </div>
        </body>
    </body>
    </html>
    """.format(SSID, config.VERSION,
                UNIQUE_ID, _uname.machine, _uname.release, _uname.version,
                _uname.lorawan, _uname.sigfox, _uname.pybytes, lora.macaddr,
                percentage_text, mcu_freq_and_temp_text,
                make_human_readable(gc.mem_free()),
                logsizetext)
    request.Response.ReturnOk(content)

# ----------------------------------------------------------------------------

@WebRoute(GET, '/lorastats')
def LoraStatistics(microWebSrv2, request):
    lora_stats = lora.lora_rec_stats
    content = """\
    <html>
    <head>
        <title>LoRa Statistics</title>
        <link rel="stylesheet" href="ttrk.css" />
    </head>
    <body>
        <h1>LoRa Stats for Node {}</h1>
        <hr/>

        <table>
        <tbody>
        <tr><td>RSSI</td><td>{} dBm</td></tr>
        <tr><td>SNR</td><td>{} dB</td></tr>
        <tr><td>SFRX</td><td>{}</td></tr>
        <tr><td>SFTX</td><td>{}</td></tr>
        <tr><td>TX Power</td><td>{} dBm</td></tr>
        <tr><td>TX Time On Air</td><td>{} ms</td></tr>
        <tr><td>TX Count</td><td>{} pkts</td></tr>
        <tr><td>TX Freq</td><td>{:,} Hz</td></tr>
        <tr><td>Bandwidth</td><td>{}</td></tr>
        <tr><td>Coding Rate</td><td>{} ({})</td></tr>
        <tr><td>Preamble</td><td>{}</td></tr>
        <tr><td>Power Mode</td><td>{}</td></tr>
        </tbody>
        </table>

        <hr/>
        <div class="flex-container">
            <a href='/'><button class='green_button'>Return</button></a>
        </div>
        </body>
    </body>
    </html>
    """.format( SSID,
                lora_stats.rssi, lora_stats.snr,
                lora_stats.sfrx, lora_stats.sftx,
                lora_stats.tx_power, lora_stats.tx_time_on_air,
                lora_stats.tx_counter, lora_stats.tx_frequency,
                config.decode_lora_bw(lora.bandwidth),
                config.decode_lora_coding_rate(lora.coding_rate),
                lora.coding_rate,
                lora.preamble,
                config.decode_lora_power_mode(lora.power_mode))
    request.Response.ReturnOk(content)

# ----------------------------------------------------------------------------

def OnWebSocketAccepted(microWebSrv2, webSocket):
    global _webSocket
    global _webJsonSocket
    LOG(' WebSocket connected:')
    LOG('   - User   : %s:%s' % webSocket.Request.UserAddress)
    LOG('   - Path   : %s'    % webSocket.Request.Path)
    LOG('   - Origin : %s'    % webSocket.Request.Origin)
    if webSocket.Request.Path.lower() == '/wscsv':
        LOG('WebSocket wscsv JOINED')
        webSocket.OnClosed = OnWebSocketClosed
        webSocket.SendTextMessage('WhoAmI,{},{}'.format(SSID, config.VERSION))
        webSocket.SendTextMessage(lora.list_group_nodes())
        webSocket.OnTextMessage = OnWebSocketTextMsg
        _webSocket = webSocket
    elif webSocket.Request.Path.lower() == '/wsjson':
        LOG('WebSocket wsjson JOINED')
        webSocket.OnClosed = OnWebJsonSocketClosed
        webSocket.OnTextMessage = OnWebJsonSocketTextMsg
        _webJsonSocket = webSocket
        LOG(lora.who_am_i(), True)
        LOG(lora.list_group_nodes(), True)

# ----------------------------------------------------------------------------

def OnWebSocketTextMsg(webSocket, msg):
    #LOG(' WebSocket text message: {}'.format(msg), True)
    lora.process_command(msg)

# ----------------------------------------------------------------------------

def OnWebJsonSocketTextMsg(webSocket, msg):
    #LOG(' JSON WebSocket message: {}'.format(msg), True)
    csvs = _json.convert_to_csv(msg)
    if csvs != None:
        #LOG(' JSON WebSocket csv: {}'.format(csvs))
        lora.process_command(csvs)
    else:
        LOG(' JSON WebSocket CSV ERROR: ' + msg)
    #lora.process_command(msg)

# ----------------------------------------------------------------------------

def OnWebSocketBinaryMsg(webSocket, msg):
    LOG(' WebSocket binary message: %s' % msg)

# ----------------------------------------------------------------------------

def OnWebSocketClosed(webSocket):
    _webSocket = None
    LOG(' WebSocket %s:%s closed' % webSocket.Request.UserAddress)

# ----------------------------------------------------------------------------

def OnWebJsonSocketClosed(webSocket):
    global _webJsonSocket
    _webSocket = None
    LOG(' JSON WebSocket %s:%s closed' % webSocket.Request.UserAddress)
    _webJsonSocket = None

# ----------------------------------------------------------------------------

def run_web_server():
    LOG(' WEB: RUN WEB SERVER')
    wlan = WLAN()

    # Set country code to North America (US)
    #
    wlan.country(country='US', schan=1, nchan=11, max_tx_pwr=-101, policy=0)

    # create and configure as an access point
    #
    wlan.init(mode=WLAN.AP, ssid=SSID, auth=(None), channel=6,
        antenna=WLAN.INT_ANT)
    LOG(' WLAN MODE: {}'.format(wlan.mode()))

    # id = 1 signifies the AP interface
    #
    LOG(wlan.ifconfig(id=1,
        config=(config.IPADDRESS, '255.255.255.0',
            config.IPADDRESS, '192.168.1.1')))

    # Set up server socket
    serversocket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)

    # ------------------------------------------------------------------------
    # Loads the WebSockets module globally and configures it.
    #
    LOG(' WEB: LOAD WEB SOCKETS.')
    wsMod = MicroWebSrv2.LoadModule('WebSockets')
    wsMod.OnWebSocketAccepted = OnWebSocketAccepted

    # Instantiates the MicroWebSrv2 class,
    #
    LOG(' WEB: INSTANTIATE MICROWEBSRV2')
    mws2 = MicroWebSrv2()

    # For embedded MicroPython, use a very light configuration,
    #
    mws2.SetEmbeddedConfig()

    # All pages not found will be redirected to the home '/',
    #
    mws2.NotFoundURL = '/'

    # Starts the server as easily as possible in managed mode,
    #
    LOG(' WEB: START MICROWEBSRV2 MANAGED.')
    mws2.StartManaged()

    while mws2.IsRunning:
        sleep(1)
    serversocket.close()
    LOG(' WEB: EXITED MICROWEBSVR2')

# ----------------------------------------------------------------------------
# Show everything we care to know about this node. This will be written as
# the first information to the log file every time the node is started or
# restarted.
#
def show_system_information():
    LOG("Reset Reason:        %s" % get_reset_cause())
    LOG("TeamTrack Version:   %s" % config.VERSION)
    LOG("Unique ID:           %s" % UNIQUE_ID)
    LOG("Machine:             %s" % os.uname().machine)
    LOG("Firmware Release:    %s" % os.uname().release)
    LOG("MicroPython Version: %s" % os.uname().version)
    LOG("LoRaWan Version:     %s" % os.uname().lorawan)
    LOG("SigFox Version:      %s" % os.uname().sigfox)
    LOG("Pybytes Version:     %s" % os.uname().pybytes)
    LOG("LoRa MACADDR:        %s" % lora.macaddr)
    LOG("WiFi SSID:           %s" % SSID)
    LOG("IP ADDRESS:          %s" % config.IPADDRESS)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
#
# MAIN
#
show_system_information()
find_i2c_devices()

_thread.start_new_thread(show_alarm_state, ())
_thread.start_new_thread(query_position, (config.TIMER_GPS, ))
_thread.start_new_thread(query_real_time_clock, (config.TIMER_RTC, ))
if config.ENABLE_BLUETOOTH:
    _thread.start_new_thread(
        bluetooth.simple_bluetooth_scan, (config.TIMER_BLUETOOTH, ))
_thread.start_new_thread(lora.send_lora_heartbeat, (get_gcoords, ))
_thread.start_new_thread(run_web_server, ())
