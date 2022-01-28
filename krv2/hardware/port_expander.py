import logging
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

from smbus2 import SMBus

LOG = logging.getLogger(__file__)


class PortExpander:
    def __init__(self):
        self._mcp23017 = MCP23017


@dataclass
class Registers:
    IODIRA = 0x00  # IO direction A - 1= input 0 = output
    IODIRB = 0x01  # IO direction B - 1= input 0 = output
    IPOLA = 0x02  # Input polarity A
    IPOLB = 0x03  # Input polarity B
    GPINTENA = 0x04  # Interrupt-onchange A
    GPINTENB = 0x05  # Interrupt-onchange B
    DEFVALA = 0x06  # Default value for port A
    DEFVALB = 0x07  # Default value for port B
    INTCONA = 0x08  # Interrupt control register for port A
    INTCONB = 0x09  # Interrupt control register for port B
    IOCON = 0x0A  # Configuration register
    GPPUA = 0x0C  # Pull-up resistors for port A
    GPPUB = 0x0D  # Pull-up resistors for port B
    INTFA = 0x0E  # Interrupt condition for port A
    INTFB = 0x0F  # Interrupt condition for port B
    INTCAPA = 0x10  # Interrupt capture for port A
    INTCAPB = 0x11  # Interrupt capture for port B
    GPIOA = 0x12  # Data port A
    GPIOB = 0x13  # Data port B
    OLATA = 0x14  # Output latches A
    OLATB = 0x15  # Output latches B


@dataclass
class Pins:
    GPA0: int = 1
    GPA1: int = 2
    GPA2: int = 4
    GPA3: int = 8
    GPA4: int = 16
    GPA5: int = 32
    GPA6: int = 64
    GPA7: int = 128
    GPB0: int = 1
    GPB1: int = 2
    GPB2: int = 4
    GPB3: int = 8
    GPB4: int = 16
    GPB5: int = 32
    GPB6: int = 64
    GPB7: int = 128


@dataclass
class Dir:
    input: int = 1
    output: int = 0


@dataclass
class OutputValue:
    high: int = 1
    low: int = 0


class Buttons(Enum):
    enc0_sw = 0
    enc1_sw = 1
    button_back = 2
    button_pause_play = 3
    button_prev_song = 4
    button_next_song = 5
    button_shuffle_repeat = 6
    button_spare = 7
    button_next_source = 8
    dummy = 9
    button_exit = 10


Pin = namedtuple("Pin", "port bit name dir default pullup interrupt")


Pins = {
    "GPB0": Pin(port="B", bit=0, name=Buttons.enc0_sw, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True),
    "GPB1": Pin(port="B", bit=1, name=Buttons.enc1_sw, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True),
    "GPB2": Pin(
        port="B", bit=2, name=Buttons.button_back, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True
    ),
    "GPB3": Pin(
        port="B", bit=3, name=Buttons.button_pause_play, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True
    ),
    "GPB4": Pin(
        port="B", bit=4, name=Buttons.button_prev_song, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True
    ),
    "GPB5": Pin(
        port="B", bit=5, name=Buttons.button_next_song, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True
    ),
    "GPB6": Pin(
        port="B",
        bit=6,
        name=Buttons.button_shuffle_repeat,
        dir=Dir.input,
        default=OutputValue.high,
        pullup=True,
        interrupt=True,
    ),
    "GPB7": Pin(
        port="B", bit=7, name=Buttons.button_spare, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True
    ),
    "GPA0": Pin(
        port="A", bit=0, name=Buttons.button_next_source, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True
    ),
    "GPA1": Pin(port="A", bit=1, name=Buttons.dummy, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True),
    "GPA2": Pin(port="A", bit=2, name=Buttons.dummy, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True),
    "GPA3": Pin(port="A", bit=3, name=Buttons.dummy, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True),
    "GPA4": Pin(port="A", bit=4, name=Buttons.dummy, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True),
    "GPA5": Pin(port="A", bit=5, name=Buttons.dummy, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True),
    "GPA6": Pin(port="A", bit=6, name=Buttons.dummy, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True),
    "GPA7": Pin(
        port="A", bit=7, name=Buttons.button_exit, dir=Dir.input, default=OutputValue.high, pullup=True, interrupt=True
    ),
}


class MCP23017:
    def __init__(self, address, pin_interface):
        self._pin_interface = pin_interface
        self._address = address
        self._output_a = 0
        self._output_b = 0
        self._directions_a = 0
        self._directions_b = 0
        self._int_en_a = 0
        self._int_en_b = 0
        self._local_defvala = 0
        self._local_defvalb = 0
        self._intcona = 0
        self._intconb = 0

    def setup_pe_defaults(self):
        self._local_defvala, dir_register, int_register, pullup_register = self.get_defaults("A")
        self.set_direction_porta(dir_register)
        self.set_default_value_porta(self._local_defvala)
        self.set_pullups_porta(pullup_register)
        self.enable_interrupt_porta(int_register)

        self._local_defvalb, dir_register, int_register, pullup_register = self.get_defaults("B")
        self.set_direction_portb(dir_register)
        self.set_default_value_portb(self._local_defvalb)
        self.set_pullups_portb(pullup_register)
        self.enable_interrupt_portb(int_register)

        self.mirror_port_interrupts()

    def poll(self) -> List[str]:
        low_values = []
        pressed_buttons = []
        if self._pin_interface.pe_hmi_interrupt:
            input_register_a, input_register_b = self.read_input()
            low_values.extend(self._get_names_of_low_pins(input_register_a, "A"))
            low_values.extend(self._get_names_of_low_pins(input_register_b, "B"))
            for low_value in low_values:
                pressed_buttons.append(Pins[low_value].name)
        LOG.debug(f"button pressed: {pressed_buttons}")
        return pressed_buttons

    @staticmethod
    def _get_names_of_low_pins(register, port) -> list:
        value = []
        if register & 128 == 0:
            value.append(f"GP{port}7")
        if register & 64 == 0:
            value.append(f"GP{port}6")
        if register & 32 == 0:
            value.append(f"GP{port}5")
        if register & 16 == 0:
            value.append(f"GP{port}4")
        if register & 8 == 0:
            value.append(f"GP{port}3")
        if register & 4 == 0:
            value.append(f"GP{port}2")
        if register & 2 == 0:
            value.append(f"GP{port}1")
        if register & 1 == 0:
            value.append(f"GP{port}0")
        return value

    @staticmethod
    def get_defaults(port: str):
        dir_register = 0
        def_register = 0
        pullup_register = 0
        int_register = 0
        for pin, props in Pins.items():
            if props.port == port:
                dir_register += props.dir << props.bit
                def_register += props.default << props.bit
                pullup_register += props.pullup << props.bit
                int_register += props.interrupt << props.bit
        print("defaults: ", def_register, dir_register, int_register, pullup_register)
        return def_register, dir_register, int_register, pullup_register

    def set_direction(self, polarity_porta: int, polarity_portb: int):
        self.set_direction_porta(polarity_porta)
        self.set_direction_portb(polarity_portb)

    def set_direction_porta(self, polarity: int):
        self._write_byte_to_register(Registers.IODIRA, polarity)

    def set_direction_portb(self, polarity: int):
        self._write_byte_to_register(Registers.IODIRB, polarity)

    def set_pullups_porta(self, pullups: int):
        self._write_byte_to_register(Registers.GPPUA, pullups)

    def set_pullups_portb(self, pullups: int):
        self._write_byte_to_register(Registers.GPPUB, pullups)

    def set_default_value_porta(self, default_value: int):
        self._local_defvala = default_value
        self._write_byte_to_register(Registers.DEFVALA, default_value)

    def set_default_value_portb(self, default_value: int):
        self._local_defvalb = default_value
        self._write_byte_to_register(Registers.DEFVALB, default_value)

    def enable_interrupt_porta(self, interrupt_mask: int):
        self._write_byte_to_register(Registers.GPINTENA, interrupt_mask)
        self._write_byte_to_register(Registers.INTCONA, interrupt_mask)

    def enable_interrupt_portb(self, interrupt_mask: int):
        self._write_byte_to_register(Registers.GPINTENB, interrupt_mask)
        self._write_byte_to_register(Registers.INTCONB, interrupt_mask)

    def mirror_port_interrupts(self):
        config_register = self._read_byte_from_register(Registers.IOCON)
        config_new = config_register | 0b01000000
        self._write_byte_to_register(Registers.IOCON, config_new)

    def read_input(self) -> tuple:
        return self._read_byte_from_register(register=Registers.GPIOA), self._read_byte_from_register(
            register=Registers.GPIOB
        )

    def get_interrupt_source(self) -> str:
        if self._pin_interface.pe_hmi_interrupt:
            source = None
            intfa = self._read_byte_from_register(Registers.INTFA)
            intcapa = self._read_byte_from_register(Registers.INTCAPA)
            source = self.get_pin_from_byte(intfa, "GPA")
            if not source:
                intfb = self._read_byte_from_register(Registers.INTFB)
                intcapb = self._read_byte_from_register(Registers.INTCAPB)
                source = self.get_pin_from_byte(intfb, "GPB")
            return source

    def get_pin_from_byte(self, byte, port: str) -> str:
        source = None
        if byte & 128:
            source = f"{port}7"
        elif byte & 64:
            source = f"{port}6"
        elif byte & 32:
            source = f"{port}5"
        elif byte & 16:
            source = f"{port}4"
        elif byte & 8:
            source = f"{port}3"
        elif byte & 4:
            source = f"{port}2"
        elif byte & 2:
            source = f"{port}1"
        elif byte & 1:
            source = f"{port}0"
        return source

    def get_pins_changed(self, input_register: int, port: str) -> list:
        if port == "GPA":
            defval = self._local_defvala
        elif port == "GPB":
            defval = self._local_defvalb
        else:
            raise ValueError(f"no such port as {port}")
        byte = input_register ^ defval
        source = []
        if byte & 128:
            source.append(f"{port}7")
        if byte & 64:
            source.append(f"{port}6")
        if byte & 32:
            source.append(f"{port}5")
        if byte & 16:
            source.append(f"{port}4")
        if byte & 8:
            source.append(f"{port}3")
        if byte & 4:
            source.append(f"{port}2")
        if byte & 2:
            source.append(f"{port}1")
        if byte & 1:
            source.append(f"{port}0")
        return source

    def _write_byte_to_register(self, register, byte):
        with SMBus(1) as bus:
            bus.write_byte_data(self._address, register, byte)

    def _read_byte_from_register(self, register):
        try:
            with SMBus(1) as bus:
                data = bus.read_byte_data(self._address, register)
        except OSError as e:
            LOG.error("Port Expander not responding! {e}")
            self._handle_i2c_error()
            data = None
        return data

    def _handle_i2c_error(self):
        self.reset_pe()
        self._setup_pe_defaults()

    def reset_pe(self):
        self._pin_interface.reset_pe()
