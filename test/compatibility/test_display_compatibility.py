from unittest.mock import Mock, patch

import pytest
from PyQt5 import QtWidgets
from pytest_mock import MockFixture
from PIL import Image

import krv2.hmi
from krv2.hmi import Hmi
from krv2.hmi.hmi_x86 import HmiX86
from krv2.hmi.hmi_arm import HmiArm
from test.utils import derive_mock_string


@pytest.mark.skip
def test_display_compatibility(mocker: MockFixture):

    GPIO = Mock()
    SMBus = Mock()
    image = Image.new(mode="1", size=(128, 64), color=0)
    hmi = HmiX86()
    for display in (0, 1):
        hmi.show_on_display(display, image)
