from time import sleep

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

from krv2.hardware.port_expander import MCP23017
from krv2.hardware.pin_interface import PinInterface

class Display:
    def __init__(self):
        serial0 = i2c(port=1, address=0x3c)
        serial1 = i2c(port=1, address=0x3d)
        device0 = sh1106(serial0)
        device1 = sh1106(serial1)

        with canvas(device0) as draw, canvas(device1) as draw1:
            draw.text((0,0), "Hi There", fill="white")
            draw1.text((0,0), "Hi There", fill="white")

        pe = MCP23017(0x20)
        for pin in ["GPA0", "GPA1"]:
            pe.pin_setup(pin, 0)
            pe.pin_output(pin, 1)
            sleep(1)
            pe.pin_setup(pin, 1)

        with canvas(device0) as draw, canvas(device1) as draw1:
            draw.text((0,0), "Hi There again", fill="white")
            draw1.text((0,0), "Hi There yep!", fill="white")

        sleep(5)

    def run_for_fun(self):
        print("hey")