try:
    import RPi.GPIO as GPIO
except ImportError:
    print("RPi.GPIO is not available. Switching to mockup mode")
    from mockups.mockupgpio import GPIO
from collections import namedtuple


class Pins:
    enc0 = {
        "a":6, # Pin 31
        "b":12 # Pin 32
    }
    enc1 = {
        "a":13, # Pin 33
        "b":26 # Pin 37
    }
    power = {
        "bst_nshdn": 17, # Pin 11
        "bst_npgood": 27, # Pin 13
        "en_front_usb_loadsw": 22, # Pin 15
        "nfault_front_usb_loadsw": 0 # Pin 27
    }
    pe = {
        "mb_ninta": 23, # Pin 16
        "hmi_ninta": 24, # Pin 18
        "nrst": 25 # Pin 22
    }


class PinInterface:
    __instance = None

    def __init__(self):
        gpio_mode = GPIO.BCM
        GPIO.setmode(gpio_mode)
        self._setup_buttons()
        self._setup_encoder_pins()
        self._setup_internal_signals()

    @staticmethod
    def _setup_buttons():
        # for button in Pins.buttons.values():
        #     GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #     GPIO.add_event_detect(button, GPIO.FALLING)
        pass

    @staticmethod
    def _setup_encoder_pins():
        for enc_pin in Pins.enc1.values():
            GPIO.setup(enc_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(enc_pin, GPIO.FALLING)

    @staticmethod
    def _setup_internal_signals():
        GPIO.setup(Pins.pe["hmi_ninta"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @property
    def pe_hmi_interrupt(self):
        return not GPIO.input(Pins.pe["hmi_ninta"])

    @property
    def hmi_ninta(self):
        return GPIO.input(Pins.pe["hmi_ninta"])


