import sys, os
import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)

from krv2.hardware.volume_control import VolumeControl


@pytest.fixture
def volume_control():
    yield VolumeControl()


def test_volume_control(volume_control):
    try:
        print("Sweeping Volume up and down. Cancel with Ctrl+C")
        while True:
            for i in range(100):
                volume_control.set(i)
    except KeyboardInterrupt:
        pass