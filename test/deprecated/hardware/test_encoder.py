from time import sleep

import sys, os
import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)

from krv2.hardware.encoder import DrehDrueck


@pytest.fixture
def encoder():
    yield DrehDrueck()


def test_encoder_readout(encoder):
    try:
        while True:
            print(encoder.read())
            sleep(0.5)
    except KeyboardInterrupt:
        pass
