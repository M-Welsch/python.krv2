import logging
from pathlib import Path
from signalslot import Signal

LOG = logging.getLogger(Path(__file__).name)

from krv2.hardware.hid import HumanInterfaceDevice
from krv2.hardware.displays import Displays


class HumanMachineInterface:

    def __init__(self, pin_interface):
        self._hid = HumanInterfaceDevice(pin_interface)
        self._hid.start()
        displays = Displays()
        self._nav = Navigation(nav_display=displays.dis1)
        self._connect_signals()

    def _connect_signals(self):
        self._hid.enc0_value_changed.connect(self._nav.on_env_val_changed)


class Navigation:
    def __init__(self, nav_display):
        self._dis = nav_display

    def on_env_val_changed(self, diff, **kwargs):
        if diff > 0:
            self._nav_down()
        if diff < 0:
            self._nav_up()

    def _nav_down(self):
        print("Pretending to navigate down")

    def _nav_up(self):
        print("Pretending to navigate up")

