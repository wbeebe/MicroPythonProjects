
def do_graphics(display, platform, SSID):
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
    display.text('-'.join(platform.split('-')[1:3]), 40, 12, 1)
    display.text(SSID, 40, 24, 1)
    display.show()
