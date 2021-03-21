from time import sleep
from PIL import ImageDraw

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106


class Displays:
    def __init__(self):
        serial0 = i2c(port=1, address=0x3c)
        serial1 = i2c(port=1, address=0x3d)
        self._device0 = sh1106(serial0)
        self._device1 = sh1106(serial1)
        self._display0 = canvas(self._device0)
        self._display1 = canvas(self._device1)

    def write_teststuff_to_displays(self):
        with canvas(self._device0) as draw, canvas(self._device1) as draw1:
            draw.text((0,0), "Hi There", fill="white")
            draw1.text((0,0), "Hi There", fill="white")

        with canvas(self._device0) as draw, canvas(self._device1) as draw1:
            draw.text((0,0), "Hi There again", fill="white")
            draw1.text((0,0), "Hi There yep!", fill="white")
        sleep(5)

    def close(self):
        raise NotImplementedError

    @property
    def dis0(self) -> ImageDraw:
        return self._display0

    @property
    def dis1(self) -> ImageDraw:
        return self._display1

    def run_for_fun(self):
        print("hey")