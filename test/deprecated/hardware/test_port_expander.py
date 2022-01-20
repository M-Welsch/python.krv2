from time import sleep

import sys, os
import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)
print(path_to_module)

from krv2.hardware.port_expander import MCP23017
from krv2.hardware.pin_interface import PinInterface


outputs = [
    "GPA0",
    "GPA1",
    "GPA2",
    "GPA3",
    "GPA4",
    "GPA5",
    "GPA6",
    "GPA7",
    "GPB0",
    "GPB1",
    "GPB2",
    "GPB3",
    "GPB4",
    "GPB5",
    "GPB6",
    "GPB7"
]

@pytest.fixture(scope="class")
def mcp():
    pin_interface = PinInterface()
    mcp23017 = MCP23017(0x20, pin_interface)
    yield mcp23017


class TestMCP23017:

    @staticmethod
    @pytest.mark.skip("never run such a test if any driver is connected to the pe's GP pins!")
    def test_outputs(mcp):
        for output in outputs:
            mcp.pin_setup(output, 0)
            mcp.pin_output(output, 1)
            sleep(0.1)
            mcp.pin_setup(output, 1)

    @staticmethod
    def test_input(mcp):
        mcp.set_direction_porta(0xFF)
        mcp.set_pullups_porta(0xff)
        mcp.set_direction_portb(0xFF)
        mcp.set_pullups_portb(0xff)
        try:
            while True:
                print(mcp.read_input())
                sleep(0.5)
        except KeyboardInterrupt:
            pass

    @staticmethod
    def test_interrupt(mcp):
        mcp.setup_pe_defaults()
        try:
            while True:
                print(mcp.get_interrupt_source())
                sleep(1)
        except KeyboardInterrupt:
            pass

    @staticmethod
    def test_poll(mcp):
        mcp.setup_pe_defaults()
        try:
            while True:
                print(mcp.poll())
                sleep(0.5)
        except KeyboardInterrupt:
            pass