from hardware.hid import HumanInterfaceDevice
from cmus_wrapper import CmusWrapper

class HumanMachineInterface:
    def __init__(self):
        self._hid = HumanInterfaceDevice()
        self._hid.start()
        self._cmus_wrapper = CmusWrapper()