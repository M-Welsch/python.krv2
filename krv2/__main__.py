import logging
from datetime import datetime
from pathlib import Path
import json
import sys, os

path_to_module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path_to_module)
print(path_to_module)

from krv2.hardware.pin_interface import PinInterface
from krv2.hmi import HumanMachineInterface

LOG = logging.getLogger(Path(__file__).name)


class Krv2:
    def __init__(self):
        pin_interface = PinInterface()
        HumanMachineInterface(pin_interface)
        self._setup_logger()

    def _setup_logger(self):
        with open("config.json", "r") as file:
            logs_directory = json.load(file)["Logging"]["logs_directory"]

        logging.basicConfig(
            filename=Path(logs_directory) / datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(name)s: %(message)s',
            datefmt='%m.%d.%Y %H:%M:%S'
        )


if __name__ == '__main__':
    Krv2()
