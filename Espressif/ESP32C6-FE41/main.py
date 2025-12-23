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

print("      Main: START")
#print("       LED: COLORS")
#import devices
#devices.cycle_colors()

import time
import bluetooth
from micropython import const
"""
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

def bt_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        # A single scan result.
        addr_type, addr, connectable, rssi, adv_data = data
        ADDR_TYPE=" PUBLIC"
        if addr_type == 1:
            ADDR_TYPE="PRIVATE"

        if adv_data == 0:
            ADV_DATA = "ADV_IND"
        elif adv_data == 1:
            ADV_DATA = "ADV_DIRECT_IND"
        elif adv_data == 2:
            ADV_DATA = "ADV_SCAN_IND"
        elif adv_data == 3:
            ADV_DATA = "ADV_NONCONN_IND"
        else:
            ADV_DATA = "SCAN_RSP"
        #print(ADDR_TYPE, connectable, rssi, adv_data)
        print(ADDR_TYPE,':'.join(['%02X' % i for i in addr]), ADV_DATA)
    elif event == _IRQ_SCAN_DONE:
        # Scan duration finished or manually stopped.
        print("       BLUETOOTH: SCAN COMPLETE")
        #print('scan complete')

print("       BLUETOOTH: SCAN")
# Scan for 10s (at 100% duty cycle)
ms_scan = 500
bt = bluetooth.BLE()
bt.irq(bt_irq)
bt.active(True)
bt.gap_scan(ms_scan, 500, 500)
time.sleep_ms(ms_scan)
"""

import asyncio
import aioble
import bluetooth

async def scan_for_bt():
    #async with aioble.scan(duration_ms=5000) as scanner:
    async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() is not None:
                print(result, " - ", result.name(), result.rssi)

async def main():
    task1 = asyncio.create_task(scan_for_bt())
    await asyncio.gather(task1)

asyncio.run(main())


print("      Main: END")
