import threading
import logging
from time import sleep
from hardware.pin_interface import PinInterface


class HumanInterfaceDevice(threading.Thread):
    def __init__(self):
        super().__init__()
        self._buttons = Buttons()
        self._exitflag = False

    def run(self):
        logging.info("Starting Human Interface Device Mainloop")
        while not self._exitflag:
            sleep(0.05)
        logging.info("Stopping Human Interface Device Mainloop")

    def terminate(self):
        self._exitflag = True


class Buttons:
    def __init__(self):
        pass

    def next_source(self):
        return None

    def prev_source(self):
        pass

    def menu_back(self):
        pass


class Encoder:
    def __init__(self):
        self._state = 0


class Potentiometer:
    def __init__(self):
        pass