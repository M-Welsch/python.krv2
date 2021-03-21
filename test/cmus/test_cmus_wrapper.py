from time import sleep
from pycmus import remote

import sys, os
import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)

from krv2.music_player.cmus_process import CmusProcess
from krv2.music_player.cmus_wrapper import CmusWrapper


@pytest.fixture(scope="class")
def cmus_wrapper():
    CmusProcess().start()
    sleep(1)
    yield CmusWrapper()


class TestCmusWrapper:
    @staticmethod
    def test_get_status_dict(cmus_wrapper):
        status_dict = cmus_wrapper.get_status_dict()
        print(status_dict)