import platform
from machine import Timer

_display = None
_ssid = None

def do_graphics(display, SSID):
    global _display, _ssid

    if _display is None:
        _display = display
    if _ssid is None:
        _ssid = SSID
    #
    # Create a graphic of the Raspberry Pi logo.
    # Display it twice, one logo for each RP2040 core,
    # similar to what the regular Raspberry Pi does on
    # initial boot.
    # I copied the bytearray for the logo from Raspberry
    # Pi itself:
    # https://github.com/raspberrypi/pico-micropython-examples/tree/master/i2c
    #
    #import framebuf
    #buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x7C\x3F\x00\x01\x86\x40\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00\x7e\xfc\x00\x00\x4c\x27\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c\x20\x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    #raspberry_pi_logo = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)
    #display.framebuf.blit(raspberry_pi_logo, 0, 33)
    #display.framebuf.blit(raspberry_pi_logo, 33, 33)
    #
    # Display the official MicroPython logo
    #
    display.framebuf.fill_rect(0, 0, 32, 32, 1)
    display.framebuf.fill_rect(2, 2, 28, 28, 0)
    display.framebuf.vline(9, 8, 22, 1)
    display.framebuf.vline(16, 2, 22, 1)
    display.framebuf.vline(23, 8, 22, 1)
    display.framebuf.fill_rect(26, 24, 2, 4, 1)
    #
    # Print some identifying text with the graphics, such
    # as version and the identifying string of the
    # Raspberry Pi Pico.
    #
    display.text('MicroPython', 40, 0, 1)
    display.text(platform.platform().split('-')[1], 40, 12, 1)
    display.text(SSID, 0, 36, 1)
    display.show()

_show_display = True

def timer_callback(t):
    global _display, _show_display
    _show_display = False
    _display.fill(0)
    _display.show()

def setup_display_blank_timer():
    timer = Timer(3)
    timer.init(period=60000, mode=Timer.ONE_SHOT, callback=timer_callback)

def toggle_display_on_off():
    global _display, _ssid, _show_display

    _show_display = not _show_display

    if _show_display:
        do_graphics(_display, _ssid)
        setup_display_blank_timer()
    else:
        _display.fill(0)
        _display.show()
