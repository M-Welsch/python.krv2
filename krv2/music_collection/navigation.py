import logging
from enum import Enum
from typing import List, Optional, Type

from krv2.music_player.mpd_wrapper import Mpd

LOG = logging.getLogger(__name__)


class ContentElement:
    def __init__(self, caption: str, artist: Optional[str], album: Optional[str] = None, track: Optional[str] = None):
        self.name = caption
        self.artist: Optional[str] = artist
        self.album: Optional[str] = album
        self.track: Optional[str] = track


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
    current_artist: Optional[str] = None
    current_album: Optional[str] = None
    current_track: Optional[str] = None

    def __init__(self, index: int, content_layer: ContentLayer, mpd: Mpd):
        self._mpd = mpd
        self.index: int = index
        self.layer: ContentLayer = content_layer
        self._content = self.build_content_list()
        self.list_size: int = self._content.size
        self.refresh_current_elements()

    @property
    def content(self) -> Content:
        return self._content

    @content.setter
    def content(self, content: Content) -> None:
        self._content = content
        # self.refresh_current_elements()

    @property
    def current(self) -> Optional[ContentElement]:
        if self._content:
            return self._content.elements[self.index]
        else:
            return None

    def __repr__(self) -> str:
        pos = f"{self.index+1}/{self.list_size}: "
        if self.current_artist:
            pos += f"{self.current_artist}"
        if self.current_album:
            pos += f" -> {self.current_album}"
        if self.current_track:
            pos += f" -> {self.current_track}"
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

    # Fixme: use this one?!
    def lower_layer(self) -> ContentLayer:
        if self.layer == ContentLayer.artist_list:
            if self._artist_has_albums():
                layer = ContentLayer.album_list
            else:
                layer = ContentLayer.track_list
        elif self.layer == ContentLayer.album_list:
            layer = ContentLayer.track_list
        else:
            raise RuntimeError(f"no such layer as {self.layer}")
        return layer

    def higher_layer(self) -> ContentLayer:
        if self.layer == ContentLayer.track_list:
            if self._artist_has_albums():
                layer = ContentLayer.album_list
            else:
                layer = ContentLayer.artist_list
        elif self.layer == ContentLayer.album_list:
            layer = ContentLayer.artist_list
        else:
            raise RuntimeError(f"no such layer as {self.layer}")
        return layer

    def reset_current_track_and_maybe_album(self) -> None:
        if self.layer == ContentLayer.artist_list:
            self.current_album = None
            self.current_track = None
        elif self.layer == ContentLayer.album_list:
            self.current_track = None

    def refresh_current_elements(self) -> None:
        if self.layer == ContentLayer.artist_list:
            self.current_artist = self.content.elements[self.index].artist
        elif self.layer == ContentLayer.album_list:
            self.current_album = self.content.elements[self.index].album
        elif self.layer == ContentLayer.track_list:
            self.current_album = self.content.elements[self.index].album
            self.current_track = self.content.elements[self.index].track

    def build_content_list(self) -> Content:
        if self.layer == ContentLayer.artist_list:
            elements = self._load_artists()
        elif self.layer == ContentLayer.album_list:
            if self._artist_has_albums():
                elements = self._load_albums_of_artist()
            else:
                elements = self._handle_no_albums()
        elif self.layer == ContentLayer.track_list:
            elements = self._load_tracks_of_album()
        else:
            raise RuntimeError(f"no such navigation layer as {self.layer}")
        content = Content(content_elements=elements)
        self.list_size = content.size
        return content

    def _handle_no_albums(self) -> List[ContentElement]:
        """returns a list of tracks and sets layer accordingly if artist has no albums, just a loose set of tracks"""
        self.layer = ContentLayer.track_list
        self.current_album = ""
        return self._load_tracks_of_artist()

    def _artist_has_albums(self) -> bool:
        return bool(self._load_albums_of_artist())

    def _load_artists(self) -> List[ContentElement]:
        artists = self._mpd.get_artists()
        elements = [ContentElement(caption=artist, artist=artist) for artist in artists]
        return elements

    def _load_albums_of_artist(self) -> List[ContentElement]:
        albums: List[str] = self._mpd.get_albums_of_artist(self.current_artist)
        return [ContentElement(caption=album, artist=self.current_artist, album=album) for album in albums]

    def _load_tracks_of_album(self) -> List[ContentElement]:
        tracks: List[str] = self._mpd.get_track_of_album_of_artist(artist=self.current_artist, album=self.current_album)
        return [
            ContentElement(caption=track, artist=self.current_artist, album=self.current_album, track=track)
            for track in tracks
        ]

    def _load_tracks_of_artist(self) -> List[ContentElement]:
        tracks: List[str] = self._mpd.get_tracks_of_artist(self.current_artist)
        return [
            ContentElement(caption=track, artist=self.current_artist, album=self.current_album, track=track)
            for track in tracks
        ]


class Navigation:
    def __init__(self, cfg_nav: dict, mpd: Mpd):
        self._mpd = mpd
        self._slice_size = cfg_nav.get("slice_size", 5)
        self._cursor = Cursor(index=0, content_layer=ContentLayer.artist_list, mpd=self._mpd)
        self._slice_range: range = self._update_list_slice()

    @property
    def current_slice(self) -> List[str]:  # Todo: test!
        current_slice_captions = []
        for item in self._update_list_slice():
            current_slice_captions.append(self._cursor.content.elements[item].name)
        return current_slice_captions

    @property
    def layer(self) -> ContentLayer:
        return self._cursor.layer

    def _update_list_slice(self) -> range:
        cursor = self._cursor.index
        slice_size = self._slice_size
        maximum = self._cursor.content.size

        if maximum < self._slice_size:
            return range(maximum)
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
            self._cursor.refresh_current_elements()
            self._cursor.content = self._cursor.build_content_list()
            self._cursor.index = 0
            print(self._cursor)

    def out(self) -> None:
        if not self._cursor.layer == ContentLayer.artist_list:
            self._cursor.layer = self._cursor.higher_layer()
            self._cursor.content = self._cursor.build_content_list()
            self._cursor.index = self._derive_cursor_index()
            self._cursor.refresh_current_elements()
            self._cursor.reset_current_track_and_maybe_album()
            print(self._cursor)

    def _derive_cursor_index(self) -> int:
        names: List[str] = [element.name for element in self._cursor.content.elements]
        if self.layer == ContentLayer.artist_list:
            index = names.index(self._cursor.current_artist)
        elif self.layer == ContentLayer.album_list:
            index = names.index(self._cursor.current_album)
        else:
            raise RuntimeError
        return index

    def __derive_cursor_index(self) -> int:
        index = 0
        lookup_map = {
            ContentLayer.artist_list: self._cursor.current_artist,
            ContentLayer.album_list: self._cursor.current_album,
        }
        try:
            names: List[str] = [element.name for element in self._cursor.content.elements]
            current_name = lookup_map[self._cursor.higher_layer()]
            if names and current_name:
                index = names.index(current_name)
        except IndexError:
            LOG.warning(f"couldn't obtain index. Current Layer = {self._cursor.layer}")
        return index
