import logging
from enum import Enum
from typing import List, Optional, Type, Union

from mishmash.orm.core import Album, Artist, Track

from krv2.music_collection import Database

LOG = logging.getLogger(__name__)


class Content:
    def __init__(self, content_elements: List[Union[Artist, Album, Track]]):
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
        self._content = self.get_new_content()
        self.list_size: int = self._content.size
        self.refresh_current_elements()

    @property
    def content(self) -> Content:
        return self._content

    @property
    def current(self) -> Optional[Union[Artist, Album, Track]]:
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
        return False

    def decrement(self) -> bool:
        if self.index > 0:
            self.index -= 1
            self.refresh_current_elements()
            return True
        return False

    def refresh_current_elements(self) -> None:
        if self.layer == ContentLayer.artist_list:
            self.current_artist = self.content.elements[self.index]
        elif self.layer == ContentLayer.album_list:
            self.current_album = self.content.elements[self.index]
        elif self.layer == ContentLayer.track_list:
            self.current_track = self.content.elements[self.index]

    def refresh_content(self) -> None:
        self._content = self.get_new_content()

    def get_new_content(self) -> Content:
        if self.layer == ContentLayer.artist_list:
            elements = self._load_artists()
        elif self.layer == ContentLayer.album_list:
            if self.current_artist.albums:
                elements = self._load_albums_of_artist()
            else:  # album list can be empty (See issue #2). Load track list instead in that case
                self.layer = ContentLayer.track_list
                elements = self._load_tracks_of_artist()
        elif self.layer == ContentLayer.track_list:
            elements = self._load_tracks_of_album()
        content = Content(content_elements=elements)
        self.list_size = content.size
        return content

    def _load_artists(self) -> List[Artist]:
        return self._db.get_all_artists()

    def _load_albums_of_artist(self) -> List[Album]:
        return self._db.get_albums_of_artist(self.current_artist)

    def _load_tracks_of_album(self) -> List[Track]:
        return self._db.get_tracks_of_album(artist=self.current_artist, album=self.current_album)

    def _load_tracks_of_artist(self) -> List[Track]:
        return self._db.get_tracks_of_artist(artist=self.current_artist)


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
            return range(maximum - slice_size, maximum)
        else:
            return range(cursor - 2, cursor + 3)

    def up(self) -> None:
        if self._cursor.decrement():
            self._update_list_slice()
            print(self._cursor)

    def down(self) -> None:
        if self._cursor.increment():
            self._update_list_slice()
            print(self._cursor)

    def into(self) -> None:
        if not self._cursor.layer == ContentLayer.track_list:
            lower_layer = {
                ContentLayer.artist_list: ContentLayer.album_list,
                ContentLayer.album_list: ContentLayer.track_list,
            }
            self._cursor.layer = lower_layer[self._cursor.layer]
            self._cursor.refresh_content()
            self._cursor.index = 0
            print(self._cursor)

    def out(self) -> None:
        if not self._cursor.layer == ContentLayer.artist_list:
            higher_layer = {
                ContentLayer.track_list: ContentLayer.album_list,
                ContentLayer.album_list: ContentLayer.artist_list,
            }
            self._cursor.layer = higher_layer[self._cursor.layer]
            self._cursor.refresh_content()
            self._cursor.index = self._derive_cursor_index()
            print(self._cursor)

    def _derive_cursor_index(self) -> int:
        lookup_map = {
            ContentLayer.artist_list: self._cursor.current_artist,
            ContentLayer.album_list: self._cursor.current_album,
        }
        try:
            db_references = [e.db_reference for e in self._cursor.content.elements]
            index_in_database_elements = db_references.index(lookup_map[self._cursor.layer])
            return index_in_database_elements
        except IndexError:
            LOG.warning("cannot get current cursor index properly")
            return 0
