from L76GNSS_EXT import L76GNSS
from machine import RTC
from pytrack import Pytrack


class GPS(L76GNSS):
    LOG = None
    rtc_set = False

    def __init__(self, logging_function, pytrack=None, sda='P22', scl='P21', timeout=None):
        super().__init__(pytrack=None, sda='P22', scl='P21', timeout=None)
        self.LOG = logging_function

    #parser for UTC time and date >> Reads GPRMC
    def parse_datetime(self):
        gps_datetime = self.get_datetime(debug=False)

        #case valid readings
        if gps_datetime[3]:
            day = int(gps_datetime[4][0] + gps_datetime[4][1] )
            month = int(gps_datetime[4][2] + gps_datetime[4][3] )
            year = int('20' + gps_datetime[4][4] + gps_datetime[4][5] )
            hour = int(gps_datetime[2][0] + gps_datetime[2][1] )
            minute = int(gps_datetime[2][2] + gps_datetime[2][3] )
            second = int(gps_datetime[2][4] + gps_datetime[2][5] )
        else:
            day, month, year, hour, minute, second = None, None, None, None, None, None

        return(day, month, year, hour, minute, second)

    def show_datetime(self):
        day, month, year, hour, minute, second = self.parse_datetime()

        if day is None:
            self.LOG(" GPS: Day is None - No DateTime")
        else:
            self.LOG(" GPS: {:02d}/{:02d}/{} - {:02d}:{:02d}:{:02d} UTC".format(
                day, month, year, hour, minute, second))

    def set_rtc(self, rtc):

        if not self.rtc_set:
            self.LOG(" GPS: RTC sync attempt to GPS time")
            day, month, year, hour, minute, second = self.parse_datetime()

            if day is None:
                self.LOG(" GPS: No timestamp from GPS")
            else:
                rtc.init((year, month, day, hour, minute, second, 0, 0))
                self.rtc_set = True
                self.LOG(" GPS: RTC sync to GPS successful")
