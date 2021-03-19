import threading
import logging
from time import sleep
from pathlib import Path

LOG = logging.getLogger(Path(__file__).name)

from krv2.hardware.port_expander import MCP23017
from krv2.hardware.encoder import DrehDrueck


class HumanInterfaceDevice(threading.Thread):
    def __init__(self, pin_interface):
        super().__init__()
        self._buttons = Buttons(pin_interface)
        self._encoder = Encoder()
        self._exitflag = False

    def run(self):
        LOG.info("Starting Human Interface Device Mainloop")
        while not self._exitflag:
            buttons = self._buttons.poll()
            val_enc0, val_enc1 = self._encoder.read()
            print(f"buttons_pressed: {buttons}, encoder 0: {val_enc0}, encoder 1: {val_enc1}")
            sleep(0.05)
            if "button_exit" in buttons:
                self._exitflag = True
        LOG.info("Stopping Human Interface Device Mainloop")

    def terminate(self):
        self._exitflag = True


class Buttons:
    def __init__(self, pin_interface):
        self._pe = MCP23017(0x20, pin_interface)
        self._pe.setup_pe_defaults()

    def poll(self) -> list:
        return self._pe.poll()


class Encoder:
    def __init__(self):
        self._encs = DrehDrueck()

    def read(self) -> tuple:
        return self._encs.read()
