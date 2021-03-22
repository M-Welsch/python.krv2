import threading
import logging
from pathlib import Path
from signalslot import Signal
from time import sleep

LOG = logging.getLogger(Path(__file__).name)

from krv2.hardware.port_expander import MCP23017
from krv2.hardware.encoder import DrehDrueck


class HumanInterfaceDevice(threading.Thread):
    enc0_value_changed = Signal()
    enc1_value_changed = Signal()
    enc0_sw_pressed = Signal()

    def __init__(self, pin_interface):
        super().__init__()
        self._buttons = Buttons(pin_interface)
        self._encoder = DrehDrueck()
        self._exitflag = False
        self._val_enc_old = [0, 0]

    @property
    def enc0_value(self):
        return self._encoder.read()[0]

    @property
    def enc1_value(self):
        return self._encoder.read()[1]

    def run(self):
        LOG.info("Starting Human Interface Device Mainloop")
        while not self._exitflag:
            self.check_encoders()
            buttons = self._buttons.poll()
            if "button_exit" in buttons:
                self._exitflag = True
            if "enc0_sw" in buttons:
                self.enc0_sw_pressed.emit()
            print(f"buttons_pressed: {buttons}, encoder 0: {self.enc0_value}, encoder 1: {self.enc1_value}")
            sleep(0.5)
            if "button_exit" in buttons:
                self._exitflag = True
        LOG.info("Stopping Human Interface Device Mainloop")

    def check_encoders(self):
        diff0 = self.value_changed(0)
        diff1 = self.value_changed(1)
        if diff0:
            self.enc0_value_changed.emit(diff=diff0)
        if diff1:
            self.enc0_value_changed.emit(diff=diff1)

    def value_changed(self, enc_index) -> int:
        current = self._encoder.read()[enc_index]
        old = self._val_enc_old[enc_index]
        diff = current - old
        if diff:
            self._val_enc_old[enc_index] = current
        return diff

    def terminate(self):
        self._exitflag = True


class Buttons:
    def __init__(self, pin_interface):
        self._pe = MCP23017(0x20, pin_interface)
        self._pe.setup_pe_defaults()

    def poll(self) -> list:
        return self._pe.poll()
