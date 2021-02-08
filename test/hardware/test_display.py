import sys, os
import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)
print(path_to_module)

from krv2.hardware.display import Display

@pytest.fixture
def display():
    yield Display()


def test_display_init(display):
    display.run_for_fun()