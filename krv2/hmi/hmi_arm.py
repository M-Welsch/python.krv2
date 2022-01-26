from time import sleep

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageDraw
from signalslot import Signal

from krv2.hardware.pin_interface import PinInterface
from krv2.hardware.port_expander import MCP23017
from krv2.hmi.hmi import Hmi


class HmiArm(Hmi):
    enc0 = Signal(args=["amount"])
    enc0_sw = Signal()
    enc1 = Signal(args=["amount"])
    enc1_sw = Signal()
    button = Signal(args=["name"])

    def __init__(self):
        pin_interface = PinInterface()
        self._mcp23017 = MCP23017(0x20, pin_interface)
        self._mcp23017.setup_pe_defaults()
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
        while True:
            self._mcp23017.poll()
            sleep(0.1)
