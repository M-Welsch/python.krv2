import logging
import sys

import pytest


def pytest_configure():
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(filename="test_logging_current.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(name)s: %(message)s",
        datefmt="%m.%d.%Y %H:%M:%S",
        handlers=[stdout_handler, file_handler],
    )
