try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO is not available. Switching to mockup mode")
    from mockups.mockupgpio import GPIO
from collections import namedtuple


class Pins:
    buttons = {
        "next_source": None,
        "button_below_next_source": None,
        "back": None,
        "pause_play": None,
        "next_song": None,
        "prev_song": None,
        "shuffle_random": None,
        "button_right_to_shuffle_random": None
    }
    sel_display_0n1 = 26 # Pin 37
    enc = {
        "a":12, # Pin 32
        "b":13, # Pin 33
        "sw":5 # Pin 29
    }


class PinInterface:
    def __init__(self):
        gpio_mode = GPIO.BCM
        GPIO.setmode(gpio_mode)
        self._setup_buttons
        self._setup_encoder_pins()
        self._setup_internal_signals

    @staticmethod
    def _setup_buttons():
        for button in Pins.buttons.values():
            GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(button, GPIO.FALLING)

    @staticmethod
    def _setup_encoder_pins():
        for enc_pin in Pins.enc.values():
            GPIO.setup(enc_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(enc_pin, GPIO.FALLING)

    @staticmethod
    def _setup_internal_signals():
        GPIO.setmode(Pins.sel_display_0n1, GPIO.OUT, initial=GPIO.LOW)


