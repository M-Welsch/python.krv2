import logging
from datetime import datetime
from pathlib import Path
import json
from hmi import HumanMachineInterface

def main():
    with open("config.json", "r") as file:
        logs_directory = json.load(file)["Logging"]["logs_directory"]

    logging.basicConfig(
        filename=Path(logs_directory) / datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'),
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(name)s: %(message)s',
        datefmt='%m.%d.%Y %H:%M:%S'
    )
    HumanMachineInterface()


if __name__ == '__main__':
    main()
