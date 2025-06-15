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

def formatted_time():
    dayname = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",]

    monthname = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December" ]

    now = time.localtime(time.time() + (-4 * 3600))
    day_name = dayname[now[6]]
    month_day = now[2]
    month_name = monthname[now[1]-1]
    year = now[0]

    hour = now[3]

    if hour < 12:
        am_pm = 'AM'
        if hour == 0:
            hour = 12
    else:
        am_pm = 'PM'
        if hour > 12:
            hour -= 12

    minutes = now[4]

    return f"{hour}:{minutes:02} {am_pm}  {day_name} {month_day} {month_name} {year}"
