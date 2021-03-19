import logging
from datetime import datetime
from pathlib import Path
import json
from hmi import HumanMachineInterface

LOG = logging.getLogger(Path(__file__).name)


class Krv2:
    def __init__(self):
        HumanMachineInterface()
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
