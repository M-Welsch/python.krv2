from time import sleep
from PIL import ImageDraw
from threading import Thread

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106


class Displays:
    def __init__(self):
        serial0 = i2c(port=1, address=0x3c)
        serial1 = i2c(port=1, address=0x3d)
        self._display0 = sh1106(serial0)
        self._display1 = sh1106(serial1)

    def write_teststuff_to_displays(self):
        with canvas(self._display0) as draw, canvas(self._display1) as draw1:
            print(f"Type(draw) = {type(draw)} <><<<<<<<<<<<<<<<<<<")
            draw.text((0,0), "Hi There", fill="white")
            draw1.text((0,0), "Hi There", fill="white")
        sleep(5)

    @property
    def dis0(self) -> ImageDraw.Draw:
        return self._display0

    @property
    def dis1(self) -> ImageDraw.Draw:
        return self._display1

    def run_for_fun(self):
        print("hey")