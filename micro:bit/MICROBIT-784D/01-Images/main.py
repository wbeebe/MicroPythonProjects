import scrollbit
from microbit import Image
from microbit import display
import time
import machine as ma
import os

UUID = ''.join("{:02X}".format(b) for b in ma.unique_id())
UNAME = os.uname().sysname.upper()
SSID = UNAME + "-" + UUID[-4:]
print(SSID)

# Set up some images to draw in succession.
images = [
    Image.CHESSBOARD,
    Image.DIAMOND_SMALL,
    Image.DIAMOND,
    Image.HEART_SMALL,
    Image.HEART,
    Image.SQUARE_SMALL,
    Image.SQUARE,
    Image.HAPPY,
    Image.SAD,
    Image.HOUSE,
    Image.PACMAN,
    Image.GHOST,
    Image.ARROW_E,
    Image.ARROW_S,
    Image.ARROW_W,
    Image.ARROW_N,
    ]

while True:
    for image in images:
        display.show(image)
        for x in range(-6,18):
            scrollbit.clear()
            scrollbit.draw_icon(x, 1, image, brightness=100)
            scrollbit.show()
            time.sleep(0.02)

# change the sleep time to change the speed the image moves