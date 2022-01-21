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

    def __init__(self, index: int, content_layer: ContentLayer, content: Optional[Content] = None):
        self.index: int = index
        self.layer: ContentLayer = content_layer
        self.content = content
        self.list_size: int = content.size if content else 0

    @property
    def current(self) -> Optional[ContentElement]:
        if self.content:
            return self.content.elements[self.index]
        else:
            return None

    @property
    def current_pos(self) -> str:
        pos = f"{self.index}/{self.list_size}: "
        if self.current_artist:
            pos += f"{self.current_artist.name}"
        if self.current_album:
            pos += f" -> {self.current_album.title}"
        if self.current_track:
            pos += f" -> {self.current_track.title}"
        return pos

    def goto_first_db_element(self):
        self.index = len(PREPENDED_COMMANDS)

    def increment(self) -> bool:
        if self.index < self.list_size - 1:
            self.index += 1
            self.refresh_current_elements()
            return True

    def decrement(self) -> bool:
        if self.index > 0:
            self.index -= 1
            self.refresh_current_elements()
            return True

    @property
    def current_artist_m(self) -> Artist:
        if isinstance(self.current, CommandElement):
            db_ref_relevant_element = self.content.elements[len(PREPENDED_COMMANDS)].db_reference
        elif isinstance(self.current, DatabaseElement):
            db_ref_relevant_element = self.current.db_reference

        if isinstance(db_ref_relevant_element, Artist):
            return db_ref_relevant_element
        elif isinstance(db_ref_relevant_element, Album) or isinstance(db_ref_relevant_element, Track):
            return db_ref_relevant_element.artist

    @property
    def current_album_m(self) -> Optional[Album]:
        db_ref_current_element = self.current.db_reference


    def refresh_current_elements(self):
        if self.layer == ContentLayer.artist_list:
            self.current_artist = self.content.elements[self.index].db_reference
        elif self.layer == ContentLayer.album_list:
            self.current_album = self.content.elements[self.index].db_reference
        elif self.layer == ContentLayer.track_list:
            self.current_track = self.content.elements[self.index].db_reference


class Navigation:
    def __init__(self, nav_config: dict, db: Database):
        self._db: Database = db
        self._slice_size = nav_config.get("slice_size", 5)
        self._cursor = Cursor(index=0, content_layer=ContentLayer.artist_list)
        self._content: Content = self.build_content_list()
        self._cursor.content = self._content
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
        if self._cursor.decrement():
            self._update_list_slice()

    def down(self):
        if self._cursor.increment():
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
            self._cursor.index = self._derive_cursor_index()

    def _derive_cursor_index(self) -> int:
        lookup_map = {
            ContentLayer.artist_list: self._cursor.current_artist,
            ContentLayer.album_list: self._cursor.current_album
        }
        try:
            db_references = [e.db_reference for e in self._content.db_elements]
            index_in_database_elements = db_references.index(lookup_map[self._cursor.layer])
            offset_due_to_command_elements = len(self._content.cmd_elements)
            return index_in_database_elements + offset_due_to_command_elements
        except IndexError:
            LOG.warning("cannot get current cursor index properly")
            return 0
