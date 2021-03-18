from dataclasses import dataclass
from math import log2
from smbus2 import SMBus


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
        self._defvala = 0
        self._defvalb = 0
        self._intcona = 0
        self._intconb = 0

    def set_polarity(self, polarity_porta: int, polarity_portb: int):
        self.set_polarity_porta(polarity_porta)
        self.set_polarity_portb(polarity_portb)

    def set_polarity_porta(self, polarity: int):
        self._write_byte_to_register(Registers.IODIRA, polarity)

    def set_polarity_portb(self, polarity: int):
        self._write_byte_to_register(Registers.IODIRB, polarity)

    def set_pullups_porta(self, pullups: int):
        self._write_byte_to_register(Registers.GPPUA, pullups)

    def set_pullups_portb(self, pullups: int):
        self._write_byte_to_register(Registers.GPPUB, pullups)

    def set_default_value_porta(self, default_value: int):
        self._write_byte_to_register(Registers.DEFVALA, default_value)

    def set_default_value_portb(self, default_value: int):
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
        return self._read_byte_from_register(register=Registers.GPIOA), \
               self._read_byte_from_register(register=Registers.GPIOB)

    def get_interrupt_source(self) -> list:
        if self._pin_interface.pe_hmi_interrupt:
            source = []
            intfa = self._read_byte_from_register(Registers.INTFA)
            intcap = self._read_byte_from_register(Registers.INTCAPA)
            source.extend(self.get_pin_from_byte(intfa, "GPA"))
            intfb = self._read_byte_from_register(Registers.INTFB)
            intcap = self._read_byte_from_register(Registers.INTCAPB)
            source.extend(self.get_pin_from_byte(intfb, "GPB"))
            return source
        else:
            return []

    @staticmethod
    def get_pin_from_byte(byte, port: str) -> list:
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


    def pin_setup(self, pin: str, direction: int, interrupt: bool=False, default_value: int = 1) -> None:
        pin_nr = int(pin[3])
        if pin.startswith("GPA"):
            self._manipulate_local_register(Registers.IODIRA, self._directions_a, pin_nr, direction)
            if interrupt:
                self._manipulate_local_register(Registers.GPINTENA, self._int_en_a, pin_nr, 1)
                self._manipulate_local_register(Registers.DEFVALA, self._defvala, pin_nr, default_value)
                self._manipulate_local_register(Registers.INTCONA, self._intcona, pin_nr, 1)
        elif pin.startswith("GPB"):
            self._manipulate_local_register(Registers.IODIRB, self._directions_b, pin_nr, direction)
        else:
            raise ValueError

    def all_inputs(self):
        self._write_byte_to_register(Registers.IODIRA, 0xFF)
        self._write_byte_to_register(Registers.IODIRB, 0xFF)

    def pin_output(self, pin: str, value: int):
        pin_nr = int(pin[3])
        if pin.startswith("GPA"):
            self._manipulate_local_register(Registers.OLATA, self._output_a, pin_nr, value)
        elif pin.startswith("GPB"):
            self._manipulate_local_register(Registers.OLATB, self._output_b, pin_nr, value)
        else:
            raise ValueError(f"Pin designators should be within GPA0-7 or GPB0-7. Received {pin} ")

    def _manipulate_local_register(self, register_ic, register_content_local_mirror, pin_nr, value):
        if value == 1:
            register_content_local_mirror = register_content_local_mirror | (1 << pin_nr)
        elif value == 0:
            register_content_local_mirror = register_content_local_mirror & ~(1 << pin_nr)
        else:
            raise ValueError("Pin output states are 0 or 1")
        self._write_byte_to_register(register_ic, register_content_local_mirror)

    def _write_byte_to_register(self, register, byte):
        with SMBus(1) as bus:
            bus.write_byte_data(self._address, register, byte)

    def _read_byte_from_register(self, register):
        with SMBus(1) as bus:
            data = bus.read_byte_data(self._address, register)
        return data

