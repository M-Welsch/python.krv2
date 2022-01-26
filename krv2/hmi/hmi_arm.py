from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageDraw
from signalslot import Signal

from krv2.hmi.hmi import Hmi


class HmiArm(Hmi):
    enc0 = Signal(args=["amount"])
    enc0_sw = Signal()
    enc1 = Signal(args=["amount"])
    enc1_sw = Signal()
    button = Signal(args=["name"])

    def __init__(self):
        self._display0 = sh1106(i2c(port=1, address=0x3C))
        self._display1 = sh1106(i2c(port=1, address=0x3D))

    @property
    def dis0(self) -> ImageDraw.Draw:
        return self._display0

    @property
    def dis1(self) -> ImageDraw.Draw:
        return self._display1

    def connect_signals(self):
        pass

    def start(self):
        pass
