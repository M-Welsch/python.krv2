import logging
from datetime import datetime
from pathlib import Path
import json
import sys
import os
from platform import machine
from signalslot import Signal

path_to_module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path_to_module)

LOG = logging.getLogger(__name__)


def setup_logger() -> None:
    with open(Path(path_to_module)/"krv2"/"config.json", "r") as file:
        logs_directory = json.load(file)["Logging"]["logs_directory"]

    logging.basicConfig(
        filename=Path(path_to_module)/"krv2"/Path(logs_directory) / datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'),
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(name)s: %(message)s',
        datefmt='%m.%d.%Y %H:%M:%S'
    )


if __name__ == '__main__':
    setup_logger()
    if machine() == 'armv7l':
        print("Raspi")
        from krv2.hmi.hmi import Hmi
        h = Hmi()
    elif machine() == 'x86_64':
        print("Laptop")
        from krv2.hmi.hmi_mockup import HmiMockup
        h = HmiMockup()
    else:
        raise ValueError("I don't know who I am!")
    h.connect_signals()
    h.start()
