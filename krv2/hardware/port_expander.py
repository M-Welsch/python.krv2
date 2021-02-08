from dataclasses import dataclass

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


class MCP23017:
    def __init__(self, address):
        self._address = address
        self._output_a = 0
        self._output_b = 0
        self._directions_a = 0
        self._directions_b = 0

    def pin_setup(self, pin: str, direction: int, interrupt: bool=False) -> None:
        pin_nr = int(pin[3])
        if pin.startswith("GPA"):
            self._manipulate_local_register(Registers.IODIRA, self._directions_a, pin_nr, direction)
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

