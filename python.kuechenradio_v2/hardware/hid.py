import threading
import logging
from time import sleep
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO is not available. Switching to mockup mode")
    from mockups.mockupgpio import GPIO


class Pinout:
    buttons = {
        "next_source" : 40,
        "prev_source" : None,
        "pause_play" : None,
        "next_song" : None,
        "prev_song" : None,
        "back" : None
    }
    enc = {
        "a":None,
        "b":None,
        "sw":None
    }


class HumanInterfaceDevice(threading.Thread):
    def __init__(self):
        super().__init__()
        GPIO.setmode(GPIO.BOARD)
        self._buttons = Buttons()
        self._exitflag = False

    def run(self):
        logging.info("Starting Human Interface Device Mainloop")
        while not self._exitflag:
            if GPIO.event_detected(Pinout.buttons["next"]):
                print("Event!!")
            sleep(0.05)
        logging.info("Stopping Human Interface Device Mainloop")

    def terminate(self):
        self._exitflag = True


class Buttons:
    def __init__(self):
        self._setup_buttons()

    def _setup_buttons(self):
        for button in Pinout.buttons.values():
            GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(button, GPIO.FALLING)

    def next_source(self):
        return None

    def prev_source(self):
        pass

    def menu_back(self):
        pass


class Encoder:
    def __init__(self):
        self._setup_encoder_pins()
        self._state = 0

    def _setup_encoder_pins(self):
        for enc_pin in Pinout.enc.values():
            GPIO.setup(enc_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(enc_pin, GPIO.FALLING)


class Potentiometer:
    def __init__(self):
        pass