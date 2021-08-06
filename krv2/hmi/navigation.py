from signalslot import Signal
from pathlib import Path
import json


class Navigation:
    refresh_nav_display = Signal()
    play_all_str = "< play all >"

    def __init__(self):
        self._lib_path = self._get_lib_path()
        self._current_path = self._lib_path
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
        with open(Path.cwd()/"python.krv2/krv2/config.json", "r") as cf:
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

    def on_enc0_pressed(self, **kwargs):
        print(f"self.path_from_cursor(): {self.path_from_cursor()}, type(self.path_from_cursor()): {type(self.path_from_cursor())}")
        if self.path_from_cursor().is_dir():
            self.into()
        elif self.path_from_cursor().is_file():
            self.play_selection()
        elif self.cursor_text == self.play_all_str:
            print("Play all. Partymode!")

    def down(self):
        new_index = self.limit(self._cursor - 1, 0, len(self._current_navigation_layer) - 1)
        print(f"updating seletion to {new_index} with content {self._current_navigation_layer[new_index]}")
        self._cursor = new_index

    def up(self):
        new_index = self.limit(self._cursor + 1, 0, len(self._current_navigation_layer) - 1)
        print(f"updating seletion to {new_index} with content {self._current_navigation_layer[new_index]}")
        self._cursor = new_index

    def into(self):
        self._current_path = self.path_from_cursor()
        path_from_cursor = self.path_from_cursor()
        print(f"navigating into {path_from_cursor}")
        self._current_navigation_layer = self.content(self._current_path)
        self._cursor = 0
        self._current_navigation_display_slice = self._update_list_slice(self._current_navigation_layer, self._cursor)
        self.refresh_nav_display.emit()

    def out(self):
        if not self._current_path == self._lib_path:
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

    def play_selection(self):
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
