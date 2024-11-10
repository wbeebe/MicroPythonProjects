"""
JSON Helper Class
"""

import ujson as json

class JsonTTrk:
    SSID = None

    def __init__(self, ssid):
        self.SSID = ssid

    def convert_to_json(self, csv):
        elements = csv.split(',')
        json = '{{"Message":"{}"'.format(elements[0])
        msg = elements[0]
        if msg == 'Heartbeat':
            json += ',"Node":"{}",'.format(elements[1])
            json += '"Alarm":"{}",'.format(elements[2])
            json += '"Power":"{}",'.format(elements[3])
            json += '"RSSI":"{}"'.format(elements[4])
            if len(elements) > 5:
                json += ',"Lat":"{}",'.format(elements[5])
                json += '"Lon":"{}",'.format(elements[6])
                json += '"Timestamp":"{}"'.format(elements[7])
            json += '}'
            return json
        elif msg == 'WhoAmI':
            json += ',"Node":"{}",'.format(elements[1])
            json += '"Version":"{}"}}'.format(elements[2])
            return json
        elif msg == 'Power':
            json += ',"Percentage":"{}"}}'.format(elements[1])
            return json
        elif msg == 'MCU':
            json += ',"Clock":"{}"'.format(elements[1])
            json += '"Temperature":"{}"}}'.format(elements[2])
            return json
        elif msg == 'Nodes':
            if len(elements) > 2:
                json += ',"Members":["{}"]}}'.format('","'.join(elements[1:]))
            else:
                json += ',"Members":["{}"]}}'.format(elements[1])
            return json
        elif msg == 'ResetAll':
            json += '}'
            return json
        elif msg == 'OutOfComm':
            json += ',"Node":"{}"}}'.format(elements[1])
            return json

        return None

    def convert_to_csv(self, json_str):
        jobj = None
        print( ' Parsing: ' + json_str)
        try:
            jobj = json.loads(json_str)
            csvs = None
            if jobj['Message'] == 'Alarm':
                csvs = 'SendAlarm,{}'.format(jobj['Node'])
            elif jobj['Message'] == 'ConfirmAlarm':
                csvs = 'ConfirmAlarm,{}'.format(jobj['Node'])
            elif jobj['Message'] == 'ResetAll':
                csvs = 'ResetAll'
            elif jobj['Message'] == 'WhoAmI':
                csvs = 'WhoAmI'
            elif jobj['Message'] == 'Nodes':
                csvs = 'Nodes'

            return csvs

        except Exception as exc:
            print(' JSON exception {}'.format(exc))
            return None
