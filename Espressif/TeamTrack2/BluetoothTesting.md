# Bluetooth Testing

For initial testing, please use the Adafruit Bluefruit Connect application.
It's available for both iOS and Android, on their respective app stores.
It works on both tablet as well as smart phone.

In the example above, Bluefruit shows a single TeamTrack FiPy device with its Bluetooth radio on. The full name on the TeamTrack FiPy devices is the same as the WiFi SSID. This is to allow quick identification.

The gray connect button to the right will connect to the device. When it does, a connect message is logged both to the REPL as well as into the log file.
When you exit from the connection, you disconnect from the FiPy, and you'll then log a disconnect message to the REPL console as well as the log file.
For further details on logging, see [LOGGING](LOGGING.md).
