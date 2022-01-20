from enum import Enum

from signalslot import Signal
from pathlib import Path
import json
from pathlib import Path
from typing import Dict, Union, Type, List, Callable, Optional
import logging

from krv2.music_collection import Database
from mishmash.orm.core import Track, Artist, Album


LOG = logging.getLogger(__name__)


class ContentElement:
    cmd: str = ""
    name: str = ""


PREPENDED_COMMANDS = ["<play all>"]


class CommandElement(ContentElement):
    def __init__(self, cmd: str):
        self.cmd: str = cmd


class DatabaseElement(ContentElement):
    def __init__(self, caption: str, db_reference: Union[Album, Artist, Track]):
        self.name = caption
        self.db_reference: Union[Album, Artist, Track] = db_reference


class Content:
    def __init__(self, database_elements: List[DatabaseElement]):
        self.elements: List[Union[CommandElement, DatabaseElement]] = [CommandElement(cmd=cmd) for cmd in PREPENDED_COMMANDS]
        self.elements.extend(database_elements)
        self.type = Type
        self.size: int = len(self.elements)

    def __repr__(self) -> str:
        complete_list = [element.cmd for element in self.elements if isinstance(element, CommandElement)]
        complete_list.extend([element.name for element in self.elements if isinstance(element, DatabaseElement)])
        return "\n".join(complete_list)

    @property
    def db_elements(self) -> List[DatabaseElement]:
        return [element for element in self.elements if isinstance(element, DatabaseElement)]

    @property
    def cmd_elements(self) -> List[CommandElement]:
        return [element for element in self.elements if isinstance(element, CommandElement)]


class ContentLayer(Enum):
    artist_list_start_letter = 0
    artist_list = 1
    album_list = 2
    track_list = 3


class Cursor:
    current_artist: Optional[Artist] = None
    current_album: Optional[Album] = None
    current_track: Optional[Track] = None

    def __init__(self, index: int, content_layer: ContentLayer):
        self.index: int = index
        self.layer: ContentLayer = content_layer
        self.list_size: int = 0

    def increment(self) -> bool:
        if self.index < self.list_size - 1:
            self.index += 1
            return True

    def decrement(self) -> bool:
        if self.index > 0:
            self.index -= 1
            return True


class Navigation:
    def __init__(self, nav_config: dict, db: Database):
        self._db: Database = db
        self._slice_size = nav_config.get("slice_size", 5)
        self._cursor = Cursor(index=0, content_layer=ContentLayer.artist_list)
        self._content: Content = self.build_content_list()
        self._slice_range: range = self._update_list_slice()

    def build_content_list(self) -> Content:
        content_buildup_instructions = {
            ContentLayer.artist_list: self._load_artists,
            ContentLayer.album_list: self._load_albums_of_artist,
            ContentLayer.track_list: self._load_tracks_of_album
        }
        elements = content_buildup_instructions[self._cursor.layer]()
        content = Content(database_elements=elements)
        self._cursor.list_size = content.size
        return content

    def _load_artists(self) -> List[DatabaseElement]:
        artists = self._db.get_all_artists()
        elements = [DatabaseElement(caption=artist.name, db_reference=artist) for artist in artists]
        return elements

    def _load_albums_of_artist(self) -> Optional[List[DatabaseElement]]:
        current_content_element: DatabaseElement = self._content.elements[self._cursor.index]
        if isinstance(current_content_element, DatabaseElement) and self._cursor.layer == ContentLayer.album_list:
            current_artist = current_content_element.db_reference
            albums: List[Album] = self._db.get_albums_of_artist(current_artist)
            self._cursor.current_artist = current_artist
            return [DatabaseElement(caption=album.title, db_reference=album) for album in albums]
        else:
            LOG.warning("will not load album list")

    def _load_tracks_of_album(self) -> List[DatabaseElement]:
        current_content_element: DatabaseElement = self._content.elements[self._cursor.index]
        if isinstance(current_content_element, DatabaseElement) and self._cursor.layer == ContentLayer.track_list:
            self._cursor.current_album = current_content_element
            tracks: List[Track] = self._db.get_tracks_of_album(artist=self._cursor.current_artist, album=self._cursor.current_album)
            return [DatabaseElement(caption=track.title, db_reference=track) for track in tracks]
        else:
            LOG.warning("will not load track list")

    def _update_list_slice(self) -> range:
        cursor = self._cursor.index
        slice_size = self._slice_size
        maximum = self._content.size

        if maximum < self._slice_size:
            return range(slice_size)
        if cursor < 3:
            return range(slice_size)
        elif cursor > (maximum - 3):
            return range(maximum-slice_size, maximum)
        else:
            return range(cursor-2, cursor+3)

    def up(self):
        if self._cursor.increment():
            self._update_list_slice()

    def down(self):
        if self._cursor.decrement():
            self._update_list_slice()

    def into(self):
        if not self._cursor.layer == ContentLayer.track_list:
            lower_layer = {
                ContentLayer.artist_list: ContentLayer.album_list,
                ContentLayer.album_list: ContentLayer.track_list
            }
            self._cursor.layer = lower_layer[self._cursor.layer]
            self._content = self.build_content_list()
            self._cursor.index = 0

    def out(self):
        if not self._cursor.layer == ContentLayer.artist_list:
            higher_layer = {
                ContentLayer.track_list: ContentLayer.album_list,
                ContentLayer.album_list: ContentLayer.artist_list
            }
            self._cursor.layer = higher_layer[self._cursor.layer]
            self._content = self.build_content_list()
            self._cursor.index = self._derivate_cursor_index()

    def _derivate_cursor_index(self) -> int:
        lookup_map = {
            ContentLayer.artist_list: self._cursor.current_artist,
            ContentLayer.album_list: self._cursor.current_album
        }
        try:
            return [e.db_reference for e in self._content.db_elements].index(lookup_map[self._cursor.layer])
        except IndexError:
            LOG.warning("cannot get current cursor index properly")
            return 0



class Navigation_:
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
