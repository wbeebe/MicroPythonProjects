# The HTML page body setup as an 'f' string.
#
# Use {{ and }} if something within HTML *actually* needs to be in brackets
# such as CSS style formatting.
#
import platform
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

    _24_to_12 = [ 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,  # AM
                  12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ] # PM

    if now[3] < 11:
        am_pm = 'AM'
    else:
        am_pm = 'PM'

    hour = _24_to_12[now[3]]
    minutes = now[4]

    return f"{hour}:{minutes:02} {am_pm} - {day_name} {month_day} {month_name} {year}"


def webpage(SSID):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-type" content="text/html;charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:," />
    <style>
    html {{
        font-family: sans_serif;
        background-color: #FFFFFF;
        display: inline-block;
        margin: 0px auto;
        text-align: center;
        }}
    h1 {{
        font-size: 35px;
        color: #D35F8D;
        word-wrap: break-word;
        }}
    h2 {{
        font-size: 20px;
        color: #5FA3D3;
        word-wrap: break-word
        }}
    p{{
        font-size: 1.5rem;
        word-wrap: break-word;
        }}
    button {{
        display: inline-block;
        width: 99%;
        border: none;
        border-radius: 5px;
        color: white;
        padding: 16px 40px;
        text-decoration: none;
        font-size: 30px;
        margin: 2px;
        cursor: pointer;
        }}
    .button-red {{
        background-color: #DC143C;
        }}
    .button-green {{
        background-color: #20A020;
        }}
    .button-blue {{
        background-color: #4080E0;
        }}
    .button-gray {{
        background-color: #404040;
        }}
    p.dotted {{
        margin: auto;
        width: 90%;
        font-size:
        25px;
        text-align: center;
        }}
    </style>
    </head>
    <body>
        <title>{SSID} Control</title>
        <h1>{SSID}</h1>
        <form accept-charset="utf-8" method="POST">
        <button class="button-green" name="LED ON"      value="ON"  type="submit">LED On</button>
        <button class="button-gray"  name="LED OFF"     value="OFF" type="submit">LED Off</button>
        <button class="button-blue"  name="DISPLAY ON"  value="ON"  type="submit">Display On</button>
        <button class="button-gray"  name="DISPLAY OFF" value="OFF" type="submit">Display Off</button>
        </form>
        <h2>{' '.join(platform.platform().split('-')[0:3])}<br/>
        {formatted_time()}</h2>
    </body>
    </html>
    """
    return html
