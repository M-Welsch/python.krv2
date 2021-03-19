import logging
from pathlib import Path

LOG = logging.getLogger(Path(__file__).name)

from krv2.hardware.hid import HumanInterfaceDevice
from krv2.hardware.display import Display


class HumanMachineInterface:
    def __init__(self, pin_interface):
        self._hid = HumanInterfaceDevice(pin_interface)
        self._hid.start()
        self._displays = Display()