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
import gc
import esp
import esp32

import config
import time_tools as ttools

"""
page() is essentially a huge Python f string.
Some parts of the web page or dynamic:
    - if there is no partition named 'vfs2' then that information isn't published
    - if there is no attached OLED display then the 'Toggled OLED' button isn't published
    - if there is no MQTT broker then the 'MQTT5 Test' button isn't published.
"""
def page(SSID, DISPLAY, MQTT):
    VFS2 = "</h2>"
    try:
        vsf2 = esp32.Partition('vfs2')
        vfs2_size = vsf2.info()[3]
        VFS2 = f"<br />vfs2 size: {vfs2_size:,} bytes</h2>"
    except:
        pass
    
    OLED_BUTTON=""
    if DISPLAY is not None:
        OLED_BUTTON="""<button class='button-oled'  name="OLED"  value="ON">Toggle OLED</button>"""

    MQTT_BUTTON=""
    if MQTT is not None:
        MQTT_BUTTON="""<button class='button-off'   name="MQTT" value="ON">MQTT Report</button>"""

    html = f"""
    <html><head><title>{SSID}</title>
    <style>
    html {{
        font-family: sans-serif;
        background-color: #FFFFFF;
        display: inline-block;
        margin: 0px auto;
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
    h2 {{font-size: 200%;color: #5FA3D3;padding-left: 15px;}}
    </style>
    </head>
    <body>
    <h1>{SSID}</h1>
    <form accept-charset="utf-8" method="POST">
    <button class='button-red'   name="RED"   value="ON">Red</button>
    <button class='button-green' name="GREEN" value="ON">Green</button>
    <button class='button-blue'  name="BLUE"  value="ON">Blue</button>
    <button class='button-gray'  name="CYCLE" value="ON">Cycle</button>
    {OLED_BUTTON}
    {MQTT_BUTTON}
    </form>
    <hr />
    <h2>{ttools.formatted_time()}</h2>
    <h2>{config.version_name} {config.compiler}</h2>
    <h2>Memory Free: {gc.mem_free():,} bytes<br />
    Flash Size: {esp.flash_size():,} bytes
    {VFS2}
    </body>
    </html>
    """
    return html
