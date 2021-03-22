from pathlib import Path
from pycmus import remote
from dataclasses import dataclass
from time import time, sleep
import logging

from krv2.common.exceptions import CmusException

LOG = logging.getLogger(Path(__file__).name)

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
        socket_path = Path("/home/pi/.config/cmus/socket")
        start = time()
        while not socket_path.exists() and time()-start < 10:
            sleep(0.01)
        try:
            self._remote = remote.PyCmus()
        except FileNotFoundError:
            LOG.error(f"Could not connect to cmus on socket: {socket_path}")
            raise CmusException(f"Could not connect to cmus on socket: {socket_path}")

    def get_status_dict(self) -> dict:
        return self._remote.get_status_dict()
