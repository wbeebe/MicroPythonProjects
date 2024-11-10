"""
 This is the class for Bluetooth functionality, from the simplest to the most
 complex.
 Instantiate this class and then call its methods based on the comments below.
 Note: Instantiating the class turns on the Bluetooth radio.
"""

import binascii
import time
from network import Bluetooth

class BluetoothTTrk:
    bluetooth = None
    SSID = None
    LOG = None

    address_type = {
        0:'PUBLIC_ADDR',
        1:'RANDOM_ADDR',
        2:'PUBLIC_RPA_ADDR',
        3:'RANDOM_RPA_ADDR'
    }

    advert_type = {
        0:'CONN_ADV',
        1:'CONN_DIR_ADV',
        2:'DISC_ADV',
        3:'NON_CONN_ADV',
        4:'SCAN_RSP'
    }

    def __init__(self, SSID, logging_function):
        self.SSID = SSID
        self.LOG = logging_function

        self.bluetooth = Bluetooth()
        self.bluetooth.set_advertisement(
            name=SSID, service_uuid=b'1234567890123456')

        self.bluetooth.callback(trigger=
            Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED,
            handler=self.connection_callback)

        self.bluetooth.advertise(True)
        #self.bluetooth.stop_scan()
        self.LOG(" BT_INIT: {}".format(SSID))

    #
    # This callback will log either a connection or disconnection.
    # That is all it does right now.
    #
    def connection_callback(self, bluetooth_evt):
        events = bluetooth_evt.events()
        if events & Bluetooth.CLIENT_CONNECTED:
            self.LOG(" BTC: CLIENT CONNECTED")
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            self.LOG(" BTC: CLIENT DISCONNECTED")

#
# Scan for Bluetooth devices.
#
    def simple_bluetooth_scan(self,delay):
        self.LOG(' BTS: STARTING SIMPLE BLUETOOTH ADVERTISEMENT SCANNER')
        self.bluetooth.stop_scan()
        #
        # We're going to use a dictionary to filter out duplicate Bluetooth
        # advertisements.
        #
        advertisements = dict()

        #
        # We want to start scanning for other Bluetooth devices. The scanning
        # period is for 10 seconds. The algorithm constantly reads in Bluetooth
        # advertisement structures continuously for that 10 second period.
        #
        while True:
            self.bluetooth.start_scan(30)
            #advertisements.clear()
            last_advertisement = None
            last_adv_name = None

            while self.bluetooth.isscanning():
                adv = self.bluetooth.get_adv()
                if adv:
                    advertisements.update({adv.mac : adv})

            #
            # We're done scanning. Now iterate the advertisements dictionary
            # and log everything we've found.
            #
            for mac in sorted(advertisements.keys()):
                #
                # Get the rest of the advertisement payload.
                #
                adv = advertisements[mac]
                adv_name = self.bluetooth.resolve_adv_data(
                    adv.data, Bluetooth.ADV_NAME_CMPL)

                if adv_name == None:
                    # If we can't identify it, then remove it from our collection.
                    advertisements.pop(mac)
                    continue

                if last_adv_name != None and last_adv_name == adv_name:
                    # Remove duplicate names, only leaving the latest.
                    advertisements.pop(last_advertisement.mac)

                last_adv_name = adv_name
                last_advertisement = adv

                # Convert the binary MACADDR into a human readable string.
                #
                res = binascii.hexlify(mac,':').decode('ascii')

                self.LOG(' BTA: {} - {} - {} - {}'.format(
                    res,
                    self.address_type[adv.addr_type],
                    self.advert_type[adv.adv_type],
                    adv_name))
                    # binascii.hexlify(value.data).decode('ascii')))

            #if len(advertisements) > 0:
            #    self.logging_function(
            #        ' BTS: {} NAMED ADVERTISEMENTS'.format(
            #        len(advertisements)))
            #else:
            #    self.logging_function(' BTS: NO NAMED ADVERTISEMENTS')

            time.sleep(delay - 15)

        #try:
        #    conn = bluetooth.connect(adv.mac)
        #    services = conn.services()
        #    for service in services:
        #        time.sleep(0.050)
        #        if type(service.uuid()) == bytes:
        #            LOG('Reading chars from service = {}'.format(service.uuid()))
        #        else:
        #            LOG('Reading chars from service = %x' % service.uuid())
        #        chars = service.characteristics()
        #        for char in chars:
        #            if (char.properties() & Bluetooth.PROP_READ):
        #                LOG(' char {} value = {}'.format(char.uuid(), char.read()))
        #    conn.disconnect()
        #    break
        #except:
        #    LOG("Error while connecting or reading from the BLE device")
        #    break
