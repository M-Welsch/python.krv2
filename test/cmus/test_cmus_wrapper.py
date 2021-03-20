from time import sleep
from pycmus import remote

import sys, os
import pytest

path_to_module = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path_to_module)

from krv2.cmus.cmus_wrapper import CmusWrapper


# @pytest.fixture(scope="class")
# def cmus_wrapper():
#     yield CmusWrapper()


# class TestCmusWrapper:
#     @staticmethod
def test_get_status_dict():
    rem = remote.PyCmus()
    print(rem.get_status_dict())

    cmus_wrapper = CmusWrapper()
    print(dir(cmus_wrapper))
    status_dict = cmus_wrapper.get_status_dict()
    print(status_dict)

if __name__ == '__main__':
    test_get_status_dict()