import logging
from datetime import datetime
from pathlib import Path
import json
import sys, os

path_to_module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path_to_module)

from krv2.hardware.pin_interface import PinInterface
from krv2.hardware.hmi import HumanMachineInterface
from krv2.cmus.cmus_wrapper import CmusWrapper

LOG = logging.getLogger(Path(__file__).name)


class Krv2:
    def __init__(self):
        pin_interface = PinInterface()
        hmi = HumanMachineInterface(pin_interface)
        cmus_wrapper = CmusWrapper()
        self._setup_logger()

    def _setup_logger(self):
        with open(Path(path_to_module)/"krv2"/"config.json", "r") as file:
            logs_directory = json.load(file)["Logging"]["logs_directory"]

        logging.basicConfig(
            filename=Path(path_to_module)/"krv2"/Path(logs_directory) / datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(name)s: %(message)s',
            datefmt='%m.%d.%Y %H:%M:%S'
        )


if __name__ == '__main__':
    Krv2()
