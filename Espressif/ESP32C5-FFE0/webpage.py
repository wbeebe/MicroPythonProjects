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
import esp
import esp32

import config
import time_tools as ttools
import dht20

"""
page() is a huge Python f string.

Some parts of the web page are dynamic:
    - if the DHT20 is working then non-zero values for temperature and humidity will be published
    - if there is no attached OLED display then the 'Toggled OLED' button isn't published
    - if there is no MQTT broker then the 'MQTT Report' button isn't published.
"""
def page(SSID, DISPLAY, MQTT, DHT20):
    
    OLED_BUTTON=""
    if DISPLAY is not None:
        OLED_BUTTON="""<button class='button-oled'  name="OLED"  value="ON">Toggle OLED</button>"""

    MQTT_BUTTON=""
    if MQTT is not None:
        MQTT_BUTTON="""<button class='button-off'   name="MQTT" value="ON">MQTT Report</button>"""
    
    fahrenheit = (DHT20.temperature * 9)/5 + 32
    temp_text = f"{DHT20.temperature:.0f}&deg;C/{fahrenheit:.0f}&deg;F"
    humi_text = f"{DHT20.humidity:.0f}%"

    html = f"""
    <html><head><title>{SSID}</title>
    <style>
    html {{
        font-family: sans-serif;
        background-color: #FFFFFF;
        display: inline-block;
        margin: 0px auto;
        }}

    .container {{
        display: flex;
        gap: 20px;
        padding: 10px;
        margin: 0 auto;
    }}

    .text-box {{
        flex: 1;
        position: relative;
    }}

    .text-box label {{
        position: absolute;
        top: -50px;
        left: 0px;
        border: 1px solid #fff;
        padding: 0 30px;
        color: #5FA3D3;
        font-weight: bold;
        font-size: 300%;
    }}

    .text-box output {{
        width: 100%;
        border: 10px solid #fff;
        padding: 0 20px;
        color: #404040;
        font-size: 500%;
    }}

    button {{
        font-size: 500%;
        font-weight: normal;
        display: inline-block;
        margin: 5px;
        padding: 20px 60px;
        width: 99%;
        height: 150px;
        justify-content: center;
        align-items: center;
        text-decoration: none;
        color: #ffffff;
        border: none;
        border-radius: 15px;
        outline: none;
        }}
    .button-red {{
        background-color: #DC143C;
        }}
    .button-green {{
        background-color: #228B22;
        }}
    .button-blue {{
        background-color: #4169E1;
        }}
    .button-gray {{
        background-color: #808080;
        }}
    .button-off {{
        background-color: #404040;
    }}
    .button-oled {{
        background-color: #4040E0;
        }}

    hr {{
        border: 0;height: 2px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));
        }}
    h1 {{font-size: 500%;color: #D35F8D;text-align: center;}}
    h2 {{font-size: 300%;color: #5FA3D3;padding-left: 15px;}}
    </style>
    </head>
    <body>
    <h1>{SSID}</h1>
    <div class="container">
        <div class="text-box">
            <label  for="temperature">Temperature</label>
            <output for="temperature">{temp_text}</output>
        </div>
        <div class="text-box">
            <label  for="humidity">Humidity</label>
            <output for="humidity">{humi_text}</output>
        </div>
    </div>
    <form accept-charset="utf-8" method="POST">
    <button class='button-gray'  name="RTH" value="READ">Temperature/Humidity</button>
    {OLED_BUTTON}
    {MQTT_BUTTON}
    </form>
    <hr />
    <h2>{ttools.formatted_time()}</h2>
    <h2>{config.version_name} {config.compiler}</h2>
    <h2>Memory Free: {gc.mem_free():,} bytes<br />
    Flash Size: {esp.flash_size():,} bytes</h2>
    </body>
    </html>
    """
    return html
