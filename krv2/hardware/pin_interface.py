from time import sleep

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("RPi.GPIO is not available. Switching to mockup mode")
    from krv2.mockups.mockupgpio import GPIO

import logging
from collections import namedtuple
from pathlib import Path

LOG = logging.getLogger(Path(__file__).name)


class Pins:
    enc0 = {"a": 4, "b": 17}  # Pin 7  # Pin 11
    enc1 = {"a": 27, "b": 22}  # Pin 13  # Pin 15
    power = {"en_front_usb_loadsw": 22, "nfault_front_usb_loadsw": 0}  # Pin 15  # Pin 27
    pe = {"mb_ninta": 23, "hmi_ninta": 24, "nrst": 25}  # Pin 16  # Pin 18  # Pin 22


class PinInterface:
    __instance = None

    def __init__(self) -> None:
        gpio_mode = GPIO.BCM
        GPIO.setmode(gpio_mode)
        self._setup_buttons()
        # self._setup_encoder_pins()
        self._setup_internal_signals()

    @staticmethod
    def _setup_buttons() -> None:
        # for button in Pins.buttons.values():
        #     GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #     GPIO.add_event_detect(button, GPIO.FALLING)
        pass

    @staticmethod
    def _setup_encoder_pins() -> None:
        for enc_pin in Pins.enc0.values():
            GPIO.setup(enc_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(enc_pin, GPIO.FALLING)
        for enc_pin in Pins.enc1.values():
            GPIO.setup(enc_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(enc_pin, GPIO.FALLING)

    @staticmethod
    def _setup_internal_signals() -> None:
        GPIO.setup(Pins.pe["hmi_ninta"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @property
    def pe_hmi_interrupt(self) -> bool:
        return not GPIO.input(Pins.pe["hmi_ninta"])

    @property
    def hmi_ninta(self) -> bool:
        return GPIO.input(Pins.pe["hmi_ninta"])

    def reset_pe(self) -> None:
        LOG.info("Resetting Port Expanders")
        GPIO.output(Pins.pe["nrst"], GPIO.LOW)
        sleep(0.1)
        GPIO.output(Pins.pe["nrst"], GPIO.HIGH)

    def cleanup(self) -> None:
        GPIO.cleanup()
