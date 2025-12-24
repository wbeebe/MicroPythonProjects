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
import gc
import time
from machine import Timer
from umqtt.robust import MQTTClient

import config as cfg
import display_tools as dtools
import dht20

MQTT_BROKER    = "192.168.0.167"
ESP32_TOPIC    = b"esp32/status"
mqttClient     = None
mqtt_msg_count = 0
SSID           = None
DHT20          = None
temp_txt       = None
humi_txt       = None

"""
publish() takes two arguments, the MQTT message type, and the data payload to send.
publish() builds the initial part of the message from the device's SSID and the date,
or time stamp, of the time publish() is called.

publish() then adds the payload at the end and sends the MQTT message out as minified JSON.

publish() has a special use case where it checks if the message type is "PING" or "PWRON".
If it is, then the payload is ignored and the minified JSON generated up to that point
is closed off and sent to the broker.

If mqttClent is None, meaning that a broker connection has not been made, then publish()
will quietly exit.

publish will return True if it successfully published to the broker, else False otherwise.
"""
MAX_COUNT = const(120)
down_count = MAX_COUNT

def publish(msg_type, payload):
    global mqttClient, mqtt_msg_count, down_count, DHT20, temp_txt, humi_txt

    if mqttClient is None:
        return False

    if DHT20 is not None:
        temperature, humidity = DHT20.read_temperature_humidity()
        temp_txt = f"\"TEMP\":\"{temperature:.0f}C\""
        humi_txt = f"\"HUMIDITY\":\"{humidity:.0f}%\""

    try:
        # time_stamp is in ISO 8601 format
        #
        now = time.localtime(time.time())
        time_stamp = f"\"DATE\":\"{now[0]:04d}-{now[1]:02d}-{now[2]:02d}T{now[3]:02d}:{now[4]:02d}:{now[5]:02d}.{now[6]:03d}Z\""

        if msg_type == 'PING' or msg_type == 'PWRON':
            full_message = "{" + f"\"{msg_type}\":\"{SSID}\",{temp_txt},{humi_txt},{time_stamp}" + "}"
        else:
            full_message = "{" + f"\"{msg_type}\":\"{SSID}\",{temp_txt},{humi_txt},{payload},{time_stamp}" + "}"
        mqttClient.publish(ESP32_TOPIC, full_message)
        mqtt_msg_count += 1
        down_count = MAX_COUNT
        gc.collect()
        return True
    except Exception as mqtt_exception:
        print(mqtt_exception)
        gc.collect()
        return False

def report():
    dtools_txt = "\"OLED\":\"None\""
    if dtools.display is not None:
        dtools_txt = "\"OLED\":\"Enabled\""
        
    version_txt = f"\"VERSION\":\"{cfg.version_name}\""
    compiler_txt = f"\"COMPILER\":\"{cfg.compiler}\""
    build_txt = f"\"BUILD_DATE\":\"{cfg.build_date}\""

    msg = f"{dtools_txt},{version_txt},{compiler_txt},{build_txt}"
    publish("REPORT", msg)

def ping_timer_callback(timer_object):
    global mqttClient, down_count
    down_count -= 1

    if down_count > 0:
        pass
    else:
        if publish("PING", "") == False:
            print("Ping Send Failed")
        down_count = MAX_COUNT

    mqttClient.check_msg()

    gc.collect()

"""
mqtt_callback() is required when the MQTT broker is initialized,
and must be in place before a broker connection is attempted.
"""
import json

def mqtt_callback(topic, message):
    print(topic, message)
    gc.collect()

"""
broker_connect() is called with the device's SSID which is stored globally
for use with other functions in this module, specifically for use by the
broker_connect() and publish() functions.

broker_connect()
    - connects to the broker defined in MQTT_BROKER using the SSID
      as a unique identifier,
    - subscribes to the topic defined in ESP32_TOPIC,
    - initializes the ping timer

broker_connect() logging is very verbose.

If broker_connect() fails to connect to the broker then mqttClient is set to None
and any attempt pubish to the broker will silently fail.
"""
def broker_connect(_SSID, _DHT20):
    global SSID
    global DHT20
    global mqttClient
    
    SSID = _SSID
    DHT20 = _DHT20
    
    try:
        print(f"      MQTT: Broker connection start from {SSID} to {MQTT_BROKER}")
        mqttClient = MQTTClient(SSID, MQTT_BROKER, keepalive=120)
        print("      MQTT: Set receive topic callback")
        mqttClient.set_callback(mqtt_callback)
        print("      MQTT: Connect Attempt")
        mqttClient.connect(clean_session=True)
        print(f"      MQTT: Subscribe to topic {ESP32_TOPIC.decode('utf8')}")
        mqttClient.subscribe(ESP32_TOPIC)
        timer = Timer(1)
        timer.init(period=1000, mode=Timer.PERIODIC, callback=ping_timer_callback)
        print(f"      MQTT: Init ping timer: {timer}")
        print(f"      MQTT: Broker connection successfull to {MQTT_BROKER}")
        publish("PWRON", "")
    except Exception as mqtt_exception:
        print(f"      MQTT: Broker connection failure to {MQTT_BROKER}")
        print(f"      MQTT: Exception: {mqtt_exception}")
        mqttClient = None
