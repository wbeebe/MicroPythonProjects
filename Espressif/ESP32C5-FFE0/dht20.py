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

"""
`dht20.py`
================================================================================
Micropython driver for the Adafruit DHT20 Temperature & Humidity Sensor

* Original Author: Kattni Rembor
* Update Author: William Beebe

Implementation Notes
--------------------

**Hardware:**

* `Adafruit DHT20 - AHT20 Pin Module - I2C:
  <https://www.adafruit.com/product/5183>`_ (Product ID: 5183)

**Software and Dependencies:**

* Micropython firmware for the DFRobot DFR1236 FireBeetle 2 ESP32-C5:
  https://micropython.org/downloads/?mcu=esp32c5
"""
import time
from machine import SoftI2C
from micropython import const

FIXED_I2CADDR:     byte = const(0x38)  # Fixed I2C address
CALIBRATE:         byte = const(0xE1)  # Calibration command
READ_DATA:         byte = const(0xAC)  # Read data command
RESET:             byte = const(0xBA)  # Device reset command
STATUS_BUSY:       byte = const(0x80)  # Is the device busy
STATUS_CALIBRATED: byte = const(0x08)  # Did the device successfully calibrate

class DHT20:
    """
    I2C interface library for the DHT20 temperature and humidity sensor.

    :param ~machine.SoftI2C i2c: The I2C bus the DHT20 is connected to.

    **Quickstart: Importing and using the DHT20 temperature sensor**

        Here is an example of using the :class:`DHT20` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            from machine import Pin, SoftI2C
            import dht20

        Once this is done you can instantiate your `SoftI2C` object and
        then instantiate your DHT20 sensor object

        .. code-block:: python

            SDA_PIN = 9
            SCL_PIN = 10
            i2c = SoftI2C(scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
            dht = dht20.DHT20(i2c)

        Now you have access to the temperature and humidity using
        the `get_temperature_humidity()` class function call.

        .. code-block:: python

            temperature, humidity = dht.read_temperature_humidity()
        
        Note that if the DHT20 fails to calibrate, then a call to
        get_temperature_humidity() will return 0, 0.

    """

    def __init__(self, i2c) -> None:
        time.sleep_ms(20)  # 20ms delay to wake up
        self.i2c = i2c
        self.data_buffer      = bytearray(6)
        self.command_buffer_1 = bytearray(1)
        self.command_buffer_3 = bytearray(3)
        self.status_buffer    = bytearray(1)
        self.reset()
        if not self.calibrate():
            raise RuntimeError("Could not calibrate")
        self.temperature = 0
        self.humidity = 0

    """ Reset the DHT20.
    """
    def reset(self) -> None:
        self.command_buffer_1[0] = RESET
        self.i2c.writeto(FIXED_I2CADDR, self.command_buffer_1)
        time.sleep_ms(20)  # 20ms delay to wake up

    """ DHT20 self-calibration.
        Return True on success, False otherwise.
    """
    def calibrate(self) -> bool:
        self.command_buffer_3[0] = CALIBRATE
        self.command_buffer_3[1] = 0x08
        self.command_buffer_3[2] = 0x00
        self.is_calibrated = False

        try:
            self.i2c.writeto(FIXED_I2CADDR, self.command_buffer_3)
        except(RuntimeError, OSError):
            print("Could not execute CALIBRATE. Calibration failed for DHT20.")
            return self.is_calibrated

        start_busy_time = time.time_ns()
        while self.status & STATUS_BUSY:
            if time.time_ns() - start_busy_time > 3:
                raise RuntimeError("Busy over 3 seconds. Calibration failed for DHT20.")
            time.sleep_ms(10)
        self.is_calibrated = self.status & STATUS_CALIBRATED
        return self.is_calibrated

    @property
    def status(self) -> byte:
        self.i2c.readfrom_into(FIXED_I2CADDR, self.status_buffer)
        return self.status_buffer[0]

    def read_temperature_humidity(self) -> int:
        if not self.is_calibrated:
            return 0,0

        self.command_buffer_3[0] = READ_DATA
        self.command_buffer_3[1] = 0x33
        self.command_buffer_3[2] = 0x00
        self.i2c.writeto(FIXED_I2CADDR, self.command_buffer_3)
        while self.status & STATUS_BUSY:
            time.sleep_ms(10)
        self.i2c.readfrom_into(FIXED_I2CADDR, self.data_buffer)

        self.humidity = (self.data_buffer[1] << 12) | (self.data_buffer[2] << 4) | (self.data_buffer[3] >> 4)
        self.humidity = (self.humidity * 100) / 0x100000
        self.temperature = ((self.data_buffer[3] & 0xF) << 16) | (self.data_buffer[4] << 8) | self.data_buffer[5]
        self.temperature = ((self.temperature * 200.0) / 0x100000) - 50
        return self.temperature, self.humidity
