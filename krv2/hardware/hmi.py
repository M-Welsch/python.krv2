from luma.core.render import canvas
import logging
from pathlib import Path
from signalslot import Signal
import json
from PIL import Image, ImageDraw, ImageFont


LOG = logging.getLogger(Path(__file__).name)

from krv2.hardware.hid import HumanInterfaceDevice
from krv2.hardware.displays import Displays


class HumanMachineInterface:

    def __init__(self, pin_interface):
        self._hid = HumanInterfaceDevice(pin_interface)
        self._hid.start()
        displays = Displays()
        self._nav_display: ImageDraw.Draw = displays.dis1
        self._nav = Navigation(nav_display=displays.dis1)
        self._connect_signals()
        self.on_refresh_nav_display()

    def _connect_signals(self):
        self._hid.enc0_value_changed.connect(self._nav.on_env_val_changed)
        self._nav.refresh_nav_display.connect(self.on_refresh_nav_display)
        self._hid.enc0_sw_pressed.connect(self._nav.on_enc0_pressed)

    def on_refresh_nav_display(self, **kwargs):
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        with canvas(self._nav_display) as nav_display:
            posy = 0
            for line in self._nav.current_slice_of_dir_content:
                if line == self._nav.cursor_text:
                    self._place_cursor(nav_display, posy)
                nav_display.text((5, posy), line, fill="white", font=fnt)
                posy += 11

    def _place_cursor(self, nav_display, posy):
        nav_display.rectangle(xy=[0, posy + 4, 2, posy + 6], fill="white")


class Navigation:
    refresh_nav_display = Signal()

    def __init__(self, nav_display):
        self._lib_path = self._get_lib_path()
        self._dis = nav_display
        self._dir_list: list = self.list_artists()
        self._dir_list_slice: list = self._initial_dir_list_slice()
        self._cursor = 0


    @staticmethod
    def _get_lib_path() -> Path:
        with open("/home/pi/python.krv2/krv2/config.json", "r") as cf:
            return Path(json.load(cf)["Music"]["lib_path"])

    @property
    def cursor(self) -> int:
        return self._cursor

    @property
    def cursor_text(self) -> str:
        return self._dir_list[self._cursor]

    def _initial_dir_list_slice(self) -> list:
        max_index = 5
        if max_index > len(self._dir_list):
            return self._dir_list
        else:
            return self._dir_list[0:max_index]

    def list_artists(self) -> list:
        return self.list_subdirs(self._lib_path)

    @staticmethod
    def list_subdirs(parent: Path) -> list:
        subdirs: list = []
        absolute_paths = [e for e in parent.iterdir() if e.is_dir()]
        for absolute_path in absolute_paths:
            subdirs.append(absolute_path.parts[-1])
        return subdirs[0:-1]  # last entry is '\n'

    @staticmethod
    def list_files(parent: Path) -> list:
        files: list = []
        absolute_paths = parent.iterdir()
        for absolute_path in absolute_paths:
            files.append(absolute_path.parts[-1])
        return files[0:-1]  # last entry is '\n'

    def on_env_val_changed(self, diff, **kwargs):
        if diff > 0:
            self._nav_down()
        if diff < 0:
            self._nav_up()
        self._dir_list_slice = self._update_list_slice(self._dir_list, self._cursor)
        self.refresh_nav_display.emit()

    def on_enc0_pressed(self, **kwargs):
        self._nav_into()

    def _nav_down(self):
        new_index = self.limit(self._cursor - 1, 0, len(self._dir_list) - 1)
        print(f"updating seletion to {new_index} with content {self._dir_list[new_index]}")
        self._cursor = new_index

    def _nav_up(self):
        new_index = self.limit(self._cursor + 1, 0, len(self._dir_list) - 1)
        print(f"updating seletion to {new_index} with content {self._dir_list[new_index]}")
        self._cursor = new_index

    def _nav_into(self):
        subdirs = self.list_subdirs(self._lib_path/Path(self.cursor_text))
        if subdirs:
            self._dir_list = subdirs
        else:
            self._dir_list = self.list_files(self._lib_path/Path(self.cursor_text))
        print(self._dir_list)
        self.refresh_nav_display.emit()

    def _nav_out(self):
        pass

    @staticmethod
    def _update_list_slice(dir_list, cursor):
        total = 5
        if len(dir_list) < total:
            return dir_list
        if cursor < 3:
            return dir_list[0:5]
        elif cursor > (len(dir_list) - 3):
            return dir_list[-5:]
        else:
            return dir_list[cursor - 2:cursor + 3]

    @property
    def current_slice_of_dir_content(self) -> list:
        return self._dir_list_slice

    @staticmethod
    def limit(num, minimum=1, maximum=255):
        """Limits input 'num' between minimum and maximum values.
        Default minimum value is 1 and maximum value is 255."""
        return max(min(num, maximum), minimum)