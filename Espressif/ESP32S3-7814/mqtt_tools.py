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
import time
from machine import Timer
from umqtt.robust import MQTTClient

MQTT_BROKER    = "192.168.0.210"
MQTT_TOPIC    = b"esp32-mqtt5/test"
mqttClient     = None
mqtt_msg_count = 0
SSID           = None

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
def publish(msg_type, payload):
    global mqttClient
    global mqtt_msg_count

    if mqttClient is None:
        return False

    try:
        # time_stamp is in ISO 8601 format
        #
        now = time.localtime(time.time())
        time_stamp = f"\"DATE\":\"{now[0]:04d}-{now[1]:02d}-{now[2]:02d}T{now[3]:02d}:{now[4]:02d}:{now[5]:02d}.{now[6]:03d}Z\""

        if msg_type == 'PING' or msg_type == 'PWRON':
            full_message = "{" + f"\"{msg_type}\":\"{SSID}\",{time_stamp}" + "}"
        else:
            full_message = "{" + f"\"{msg_type}\":\"{SSID}\",{payload},{time_stamp}" + "}"
        mqttClient.publish(MQTT_TOPIC, full_message)
        mqtt_msg_count += 1
        return True
    except Exception as mqtt_exception:
        print(mqtt_exception)
        return False

def ping_timer_callback(timer_object):
    if publish("PING", "") == False:
        print("Ping Send Fail: " + mqtt_message)

"""
mqtt_callback() is a dummy function at this point that does nothing.
It is here because it's required when the MQTT broker is initialized,
and must be in place before a broker connection is attempted.
"""
def mqtt_callback(topic, message):
    print((topic, message))

"""
broker_connect() is called with the device's SSID which is stored globally
for use with other functions in this module, specifically for use by the
broker_connect() and publish() functions.

broker_connect()
    - connects to the broker defined in MQTT_BROKER using the SSID
      as a unique identifier,
    - subscribes to the topic defined in MQTT_TOPIC,
    - initializes the ping timer

broker_connect() logging is very verbose.

If broker_connect() fails to connect to the broker then mqttClient is set to None
and any attempt pubish to the broker will silently fail.
"""
def broker_connect(_SSID):
    global SSID
    global mqttClient

    SSID = _SSID
    try:
        print(f"      MQTT: Broker connection start from {SSID} to {MQTT_BROKER}")
        mqttClient = MQTTClient(SSID, MQTT_BROKER, keepalive=120)
        print("      MQTT: Set callback")
        mqttClient.set_callback(mqtt_callback)
        print("      MQTT: Connect")
        mqttClient.connect()
        print(f"      MQTT: Subscribe to topic {MQTT_TOPIC}")
        mqttClient.subscribe(MQTT_TOPIC)
        timer = Timer(3)
        timer.init(period=60000, mode=Timer.PERIODIC, callback=ping_timer_callback)
        print(f"      MQTT: Init ping timer: {timer}")
        print(f"      MQTT: Broker connection successful to {MQTT_BROKER}")
        publish("PWRON", "")
    except Exception as mqtt_exception:
        print(f"      MQTT: Broker connection failure to {MQTT_BROKER}")
        print(f"      MQTT: Exception: {mqtt_exception}")
        mqttClient = None

