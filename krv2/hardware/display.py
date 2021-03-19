from time import sleep

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106


class Display:
    def __init__(self):
        serial0 = i2c(port=1, address=0x3c)
        serial1 = i2c(port=1, address=0x3d)
        device0 = sh1106(serial0)
        device1 = sh1106(serial1)

        with canvas(device0) as draw, canvas(device1) as draw1:
            draw.text((0,0), "Hi There", fill="white")
            draw1.text((0,0), "Hi There", fill="white")

        with canvas(device0) as draw, canvas(device1) as draw1:
            draw.text((0,0), "Hi There again", fill="white")
            draw1.text((0,0), "Hi There yep!", fill="white")

        sleep(5)

    def run_for_fun(self):
        print("hey")