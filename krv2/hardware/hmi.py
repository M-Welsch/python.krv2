from luma.core.render import canvas
import logging
from pathlib import Path
from signalslot import Signal
import json
from PIL import Image, ImageDraw, ImageFont

from krv2.hardware.displays import Displays
from krv2.hardware.hid import HumanInterfaceDevice

LOG = logging.getLogger(Path(__file__).name)


class HumanMachineInterface:

    def __init__(self, pin_interface):
        self._hid = HumanInterfaceDevice(pin_interface)
        self._hid.start()
        displays = Displays()
        self._nav_display: ImageDraw.Draw = displays.dis1
        self._nav = Navigation(nav_display=displays.dis1)
        self._connect_signals()
        self.on_refresh_nav_display()

    @property
    def nav(self):
        return self._nav

    def _connect_signals(self):
        self._hid.enc0_value_changed.connect(self._nav.on_env_val_changed)
        self._nav.refresh_nav_display.connect(self.on_refresh_nav_display)
        self._hid.enc0_sw_pressed.connect(self._nav.on_enc0_pressed)
        self._hid.button_back_pressed.connect(self._nav.on_button_back_pressed)

    def on_refresh_nav_display(self, **kwargs):
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        with canvas(self._nav_display) as nav_display:
            posy = 0
            for line in self._nav.current_slice_of_dir_content:
                line = str(line)
                if line == self._nav.cursor_text:
                    self._place_cursor(nav_display, posy)
                nav_display.text((5, posy), line, fill="white", font=fnt)
                posy += 11

    def _place_cursor(self, nav_display, posy):
        nav_display.rectangle(xy=[0, posy + 4, 2, posy + 6], fill="white")


class Navigation:
    play_url = Signal()
    play_all_within_dir = Signal()
    refresh_nav_display = Signal()
    play_all_str = "< play all >"

    def __init__(self, nav_display):
        self._lib_path = self._get_lib_path()
        self._current_path = self._lib_path
        self._dis = nav_display
        self._current_navigation_layer: list = self.content(self._lib_path)
        self._current_navigation_display_slice: list = self._initial_dir_list_slice()
        self._cursor = 0

    def content(self, parent: Path) -> list:
        content: list = [self.play_all_str]
        absolute_paths = parent.iterdir()
        for absolute_path in sorted(absolute_paths):
            content.append(absolute_path.relative_to(parent))
        print(f"content: {content}")
        return content

    @staticmethod
    def _get_lib_path() -> Path:
        with open(Path.cwd()/"config.json", "r") as cf:
            return Path(json.load(cf)["Music"]["lib_path"])

    @property
    def cursor(self) -> int:
        return self._cursor

    @property
    def cursor_text(self) -> str:
        return str(self._current_navigation_layer[self._cursor])

    @property
    def current_path(self):
        return self._current_path

    def path_from_cursor(self) -> Path:
        return self._current_path/Path(self._current_navigation_layer[self._cursor])

    def _initial_dir_list_slice(self) -> list:
        max_index = 5
        if max_index > len(self._current_navigation_layer):
            return self._current_navigation_layer
        else:
            return self._current_navigation_layer[0:max_index]

    def on_env_val_changed(self, diff, **kwargs):
        if diff > 0:
            self._nav_down()
        if diff < 0:
            self._nav_up()
        self._current_navigation_display_slice = self._update_list_slice(self._current_navigation_layer, self._cursor)
        self.refresh_nav_display.emit()

    def on_enc0_pressed(self, **kwargs):
        print(f"self.path_from_cursor(): {self.path_from_cursor()}, type(self.path_from_cursor()): {type(self.path_from_cursor())}")
        if self.path_from_cursor().is_dir():
            self._nav_into()
        elif self.path_from_cursor().is_file():
            self.play_selected_item()
        elif self.cursor_text == self.play_all_str:
            print(f"Partymode! Play all within {self._current_path}")
            self.play_all_within_dir.emit(url=self._current_path)


    def on_button_back_pressed(self, **kwargs):
        if not self._current_path == self._lib_path:
            self._nav_out()

    def _nav_down(self):
        new_index = self.limit(self._cursor - 1, 0, len(self._current_navigation_layer) - 1)
        print(f"updating seletion to {new_index} with content {self._current_navigation_layer[new_index]}")
        self._cursor = new_index

    def _nav_up(self):
        new_index = self.limit(self._cursor + 1, 0, len(self._current_navigation_layer) - 1)
        print(f"updating seletion to {new_index} with content {self._current_navigation_layer[new_index]}")
        self._cursor = new_index

    def _nav_into(self):
        self._current_path = self.path_from_cursor()
        path_from_cursor = self.path_from_cursor()
        print(f"navigating into {path_from_cursor}")
        self._current_navigation_layer = self.content(self._current_path)
        self._cursor = 0
        self._current_navigation_display_slice = self._update_list_slice(self._current_navigation_layer, self._cursor)
        self.refresh_nav_display.emit()

    def _nav_out(self):
        recent_path = self._current_path
        self._current_path = self._current_path.parent
        self._current_navigation_layer = self.content(self._current_path)
        self._cursor = 0
        count = 0
        for item in self._current_navigation_layer:
            if str(item) == str(recent_path.relative_to(self._current_path)):
                self._cursor = count
            count += 1
        self._current_navigation_display_slice = self._update_list_slice(self._current_navigation_layer, self._cursor)
        self.refresh_nav_display.emit()

    def play_selected_item(self):
        self.play_url.emit(url=self.path_from_cursor())
        print("Playing selection!")

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
        return self._current_navigation_display_slice

    @staticmethod
    def limit(num, minimum=1, maximum=255):
        """Limits input 'num' between minimum and maximum values.
        Default minimum value is 1 and maximum value is 255."""
        return max(min(num, maximum), minimum)
