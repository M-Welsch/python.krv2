from enum import Enum

from typing import Union, Type, List, Optional
import logging

from krv2.music_collection import Database
from mishmash.orm.core import Track, Artist, Album


LOG = logging.getLogger(__name__)


class ContentElement:
    def __init__(self, caption: str, db_reference: Union[Album, Artist, Track]):
        self.name = caption
        self.db_reference: Union[Album, Artist, Track] = db_reference


class Content:
    def __init__(self, content_elements: List[ContentElement]):
        self.elements = content_elements
        self.type = Type
        self.size: int = len(self.elements)

    def __repr__(self) -> str:
        return "\n".join([element.name for element in self.elements])


class ContentLayer(Enum):
    artist_list_start_letter = 0
    artist_list = 1
    album_list = 2
    track_list = 3


class Cursor:
    current_artist: Optional[Artist] = None
    current_album: Optional[Album] = None
    current_track: Optional[Track] = None

    def __init__(self, index: int, content_layer: ContentLayer, db: Database):
        self._db = db
        self.index: int = index
        self.layer: ContentLayer = content_layer
        self._content = self.build_content_list()
        self.list_size: int = self._content.size
        self.refresh_current_elements()

    @property
    def content(self) -> Content:
        return self._content

    @content.setter
    def content(self, content) -> None:
        self._content = content
        self.refresh_current_elements()

    @property
    def current(self) -> Optional[ContentElement]:
        if self._content:
            return self._content.elements[self.index]
        else:
            return None

    def __repr__(self) -> str:
        pos = f"{self.index}/{self.list_size}: "
        if self.current_artist:
            pos += f"{self.current_artist.name}"
        if self.current_album:
            pos += f" -> {self.current_album.title}"
        if self.current_track:
            pos += f" -> {self.current_track.title}"
        return pos

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

    def refresh_current_elements(self):
        if self.layer == ContentLayer.artist_list:
            self.current_artist = self.content.elements[self.index].db_reference
        elif self.layer == ContentLayer.album_list:
            self.current_album = self.content.elements[self.index].db_reference
        elif self.layer == ContentLayer.track_list:
            self.current_track = self.content.elements[self.index].db_reference

    def build_content_list(self) -> Content:
        content_buildup_instructions = {
            ContentLayer.artist_list: self._load_artists,
            ContentLayer.album_list: self._load_albums_of_artist,
            ContentLayer.track_list: self._load_tracks_of_album
        }
        elements = content_buildup_instructions[self.layer]()
        content = Content(content_elements=elements)
        self.list_size = content.size
        return content

    def _load_artists(self) -> List[ContentElement]:
        artists = self._db.get_all_artists()
        elements = [ContentElement(caption=artist.name, db_reference=artist) for artist in artists]
        return elements

    def _load_albums_of_artist(self) -> Optional[List[ContentElement]]:
        if self.layer == ContentLayer.album_list:
            albums: List[Album] = self._db.get_albums_of_artist(self.current_artist)
            return [ContentElement(caption=album.title, db_reference=album) for album in albums]
        else:
            LOG.warning("will not load album list")

    def _load_tracks_of_album(self) -> List[ContentElement]:
        if self.layer == ContentLayer.track_list:
            tracks: List[Track] = self._db.get_tracks_of_album(artist=self.current_artist, album=self.current_album)
            return [ContentElement(caption=track.title, db_reference=track) for track in tracks]
        else:
            LOG.warning("will not load track list")


class Navigation:
    def __init__(self, cfg_nav: dict, db: Database):
        self._db: Database = db
        self._slice_size = cfg_nav.get("slice_size", 5)
        self._cursor = Cursor(index=0, content_layer=ContentLayer.artist_list, db=self._db)
        self._slice_range: range = self._update_list_slice()

    @property
    def current_slice(self) -> List[str]:  # Todo: test!
        current_slice_captions = []
        for item in self._update_list_slice():
            current_slice_captions.append(self._cursor.content.elements[item].name)
        return current_slice_captions

    def _update_list_slice(self) -> range:
        cursor = self._cursor.index
        slice_size = self._slice_size
        maximum = self._cursor.content.size

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
            print(self._cursor)

    def down(self):
        if self._cursor.increment():
            self._update_list_slice()
            print(self._cursor)

    def into(self):
        if not self._cursor.layer == ContentLayer.track_list:
            lower_layer = {
                ContentLayer.artist_list: ContentLayer.album_list,
                ContentLayer.album_list: ContentLayer.track_list
            }
            self._cursor.layer = lower_layer[self._cursor.layer]
            self._cursor.content = self._cursor.build_content_list()
            self._cursor.index = 0
            print(self._cursor)

    def out(self):
        if not self._cursor.layer == ContentLayer.artist_list:
            higher_layer = {
                ContentLayer.track_list: ContentLayer.album_list,
                ContentLayer.album_list: ContentLayer.artist_list
            }
            self._cursor.layer = higher_layer[self._cursor.layer]
            self._cursor.content = self._cursor.build_content_list()
            self._cursor.index = self._derive_cursor_index()
            print(self._cursor)

    def _derive_cursor_index(self) -> int:
        lookup_map = {
            ContentLayer.artist_list: self._cursor.current_artist,
            ContentLayer.album_list: self._cursor.current_album
        }
        try:
            db_references = [e.db_reference for e in self._cursor.content.elements]
            index_in_database_elements = db_references.index(lookup_map[self._cursor.layer])
            return index_in_database_elements
        except IndexError:
            LOG.warning("cannot get current cursor index properly")
            return 0
