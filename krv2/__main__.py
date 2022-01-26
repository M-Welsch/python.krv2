import logging
from datetime import datetime
from pathlib import Path
from platform import machine

import yaml

from krv2.hmi.logic import Logic

LOG = logging.getLogger(__name__)


def setup_logger(cfg_log: dict) -> None:
    logging.basicConfig(
        filename=Path(cfg_log["path"]) / datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log"),
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(name)s: %(message)s",
        datefmt="%m.%d.%Y %H:%M:%S",
    )


if __name__ == "__main__":
    with open("config.yml", "r") as cf:
        cfg = yaml.safe_load(cf)
    setup_logger(cfg["log"])

    if machine() in ["armv6l", "armv7l"]:
        print("Raspi")
        from krv2.hmi.hmi_arm import HmiArm

        h = HmiArm()
    elif machine() == "x86_64":
        print("Laptop")
        from krv2.hmi.hmi_x86 import HmiX86

        h = HmiX86()
    else:
        raise ValueError("I don't know who I am! Problably the hardware platform is not supported (yet)!")
    Logic(hmi=h, cfg_logic=cfg["logic"])

# create symlink for mockup: sudo ln -s /home/max/Music /home/pi
