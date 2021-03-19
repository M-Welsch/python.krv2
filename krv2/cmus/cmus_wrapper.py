import pycmus
from dataclasses import dataclass


@dataclass
class PlaybackFrom:
    playlist: str = "playlist"
    library: str = "library"
    queue: str = "queue"


@dataclass()
class PlayScope:
    library: str = "library"
    artist: str = "artist"
    album: str = "album"


class CmusWrapper():
    def __init__(self):
        self._playing = False

    def pause_playback(self):
        pass

    def resume_playback(self):
        pass

    def next_track(self):
        pass

    def previous_track(self):
        pass

    def set_playmode(self, mode: str):
        pass