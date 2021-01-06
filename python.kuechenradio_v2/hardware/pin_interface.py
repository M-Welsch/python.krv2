try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO is not available. Switching to mockup mode")
    from mockups.mockupgpio import GPIO
from collections import namedtuple


class Pins:
    sel_display_0n1 = 26 # Pin 37
    buttons = {
        "next_source" : None,
        "prev_source" : None,
        "pause_play" : None,
        "next_song" : None,
        "prev_song" : None,
        "back" : None
    }
    enc = {
        "a":12, # Pin 32
        "b":13, # Pin 33
        "sw":5, # Pin 29
    }


class PinInterface:
    def __init__(self):
        gpio_mode = GPIO.BCM
        GPIO.setmode(gpio_mode)
        self._setup_buttons
        self._setup_encoder_pins()
        self._setup_internal_signals

    def _setup_buttons(self):
        for button in Pins.buttons.values():
            GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(button, GPIO.FALLING)

    def _setup_encoder_pins(self):
        for enc_pin in Pinout.enc.values():
            GPIO.setup(enc_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(enc_pin, GPIO.FALLING)

    def _setup_internal_signals(self):
        GPIO.setmode(Pins.sel_display_0n1, GPIO.OUT, initial = GPIO.LOW)
