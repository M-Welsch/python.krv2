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

    def on_play_selection(self, url, **kwargs):
        LOG.debug("clearing playlist ...")
        self.clear_playlist()
        LOG.debug(f"playlist cleared. Adding tracks from {url} to playlist")
        self.add_to_playlist(url)

    def get_status_dict(self) -> dict:
        return self._remote.get_status_dict()

    def play(self, url, **kwargs):
        self._remote.player_play_file(url)

    def add_to_play_queue(self, url, **kwargs):
        self._remote.send_cmd(f"add -Q {url}")

    def add_to_playlist(self, url, **kwargs):
        command = f"add -p {url}"
        LOG.debug(f"sending command {command}")
        self._remote.send_cmd(command)

    def aaa_mode_all(self):
        self.aaa_mode('all')

    def aaa_mode_artist(self):
        self.aaa_mode('artist')

    def aaa_mode_artist(self):
        self.aaa_mode('album')

    def aaa_mode(self, mode):
        if mode in ['all', 'artist', 'album']:
            self._remote.send_cmd(f"set aaa_mode {mode}")
        else:
            LOG.warning(f"no such aaa_mode as {mode}")

    def shuffle(self, active: bool):
        self._remote.send_cmd(f"set shuffle={active}")

    def repeat(self, active: bool):
        self._remote.send_cmd(f"set repeat")

    def goto_view(self, view: int):
        if view in [1, 2, 3, 4, 5, 6, 7]:
            self._remote.send_cmd(f"view {view}")

    def clear_playlist(self):
        pl_path = Path("/home/pi/.config/cmus/empty.pl")
        # with open(pl_path, "w") as playlist_file:
        #     pass
        self._remote.send_cmd(f"load -p {pl_path}")