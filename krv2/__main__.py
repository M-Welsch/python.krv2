import logging
from datetime import datetime
from pathlib import Path

import yaml
from platform import machine

from krv2.hmi.logic import Logic

LOG = logging.getLogger(__name__)


def setup_logger() -> None:
    with open("config.yml", "r") as cf:
        cfg = yaml.safe_load(cf)

    logging.basicConfig(
        filename=Path(cfg["log"]["path"]) / datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log'),
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
        from krv2.hmi.hmi_mockup import Hmi
        h = Hmi()
    else:
        raise ValueError("I don't know who I am!")
    Logic(hmi=h)

# create symlink for mockup: sudo ln -s /home/max/Music /home/pi
