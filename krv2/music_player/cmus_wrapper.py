from pycmus import remote
from dataclasses import dataclass


"""
IMPORTANT!!

when pycmus is used as root, it won't find the default socket path, so it has to be provided.
make sure, music_player itself is being started with

$ music_player --listen /home/pi/.config/music_player/socket
(or whatever the path to the socket file shall be)
"""


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


class CmusWrapper:
    def __init__(self):
        socket_path = "/home/pi/.config/cmus/socket"
        self._remote = remote.PyCmus()

    def get_status_dict(self) -> dict:
        return self._remote.get_status_dict()
