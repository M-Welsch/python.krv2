import os
import sys
from typing import Generator

import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)
print(path_to_module)

from krv2.hardware.displays import Displays


@pytest.fixture
def display() -> Generator[Displays, None, None]:
    yield Displays()


@pytest.mark.onraspi
def test_display_init(display):
    display.write_teststuff_to_displays()
