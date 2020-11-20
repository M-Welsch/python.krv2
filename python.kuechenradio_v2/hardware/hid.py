import threading
import logging
from time import sleep
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO is not available. Switching to mockup mode")
    from mockups.mockupgpio import GPIO


class HumanInterfaceDevice(threading.Thread):
    def __init__(self):
        super().__init__()
        GPIO.setmode(GPIO.BOARD)
        self._buttons = Buttons(GPIO)
        self._exitflag = False

    def run(self):
        logging.info("Starting Human Interface Device Mainloop")
        while not self._exitflag:
            if GPIO.event_detected(21):
                print("Event!!")
            sleep(0.05)
        logging.info("Stopping Human Interface Device Mainloop")

    def terminate(self):
        self._exitflag = True


class Buttons:
    def __init__(self, gpio):
        self._gpio = gpio
        self._setup_buttons()

    def _setup_buttons(self):
        GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(21, GPIO.FALLING)

    def next_source(self):
        return self._gpio.input()

    def prev_source(self):
        pass

    def menu_back(self):
        pass


class Encoder:
    def __init__(self, gpio):
        self._gpio = gpio


class Potentiometer:
    def __init__(self, gpio):
        self._gpio = gpio