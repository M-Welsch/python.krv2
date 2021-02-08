from time import sleep

import sys, os
import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)
print(path_to_module)

from krv2.hardware.port_expander import MCP23017


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


#@pytest.mark.skip("never run such a test if any driver is connected to the pe's GP pins!")
def test_outputs():
    mcp = MCP23017(0x20)
    for output in outputs:
        mcp.pin_setup(output, 0)
        mcp.pin_output(output, 1)
        sleep(0.1)
        mcp.pin_setup(output, 1)
