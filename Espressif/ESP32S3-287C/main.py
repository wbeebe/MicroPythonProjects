import platform
print(platform.platform())

import esp
print(f"Flash size {esp.flash_size():,} bytes")

import gc
print(f"Memory free {gc.mem_free():,} bytes")

from webserver import WebServer
web = WebServer()
web.run()