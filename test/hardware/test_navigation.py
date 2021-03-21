from time import sleep
import sys, os
import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)

from krv2.hardware.pin_interface import PinInterface
from krv2.hardware.hmi import HumanMachineInterface, Navigation


@pytest.fixture(scope="class")
def hmi():
    pin = PinInterface()
    yield HumanMachineInterface(pin)


class TestHmi:
    @staticmethod
    def test_navigation(hmi):
        print("Rotate the Encoder Up and down. Exit with ctrl+c")
        try:
            while True:
                sleep(0.1)
        except KeyboardInterrupt:
            pass