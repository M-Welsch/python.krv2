import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from mpd import MPDClient, ConnectionError

LOG = logging.getLogger(__name__)


MPD_DEFAULT_HOST = "localhost"
MPD_DEFAULT_PORT = 6600
MPD_DEFAULT_SOCKET = Path("/var/run/mpd/socket")
MPD_DEFAULT_TIMEOUT = 10


@dataclass
class ConnectionParams:
    host: str = MPD_DEFAULT_HOST
    port: int = MPD_DEFAULT_PORT
    socket: Path = MPD_DEFAULT_SOCKET
    timeout: float = MPD_DEFAULT_TIMEOUT

    @classmethod
    def from_cfg(cls, cfg_mpd: dict):
        c = cls()
        for param in ["host", "port", "socket"]:
            try:
                setattr(c, param, cfg_mpd[param])
            except KeyError:
                print(f"MPD connection parameter {param} not in config file. Defaulting to {getattr(cls, param)}")
        return c


@dataclass
class Stats:
    uptime: int
    playtime: int
    artists: int
    albums: int
    songs: int
    db_playtime: int
    db_update: int

    @classmethod
    def from_client(cls, client: MPDClient):
        stats = client.stats()
        return cls(
            uptime=int(stats["uptime"]),
            playtime=int(stats["playtime"]),
            artists=int(stats["artists"]),
            albums=int(stats["albums"]),
            songs=int(stats["songs"]),
            db_playtime=int(stats["db_playtime"]),
            db_update=int(stats["db_update"])
        )


@dataclass
class Status:
    @classmethod
    def from_client(cls, client: MPDClient):
        ...
        return cls()


def setup_client(conn_params: ConnectionParams) -> MPDClient:
    client = MPDClient()
    client.timeout = conn_params.timeout
    return client


class Mpd:
    def __init__(self, cfg_mpd: dict):
        self._conn_params = ConnectionParams.from_cfg(cfg_mpd)
        self._client: MPDClient = setup_client(self._conn_params)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()
        self._client.disconnect()

    def connect(self):
        self._client.connect(host=self._conn_params.host, port=self._conn_params.port)

    def artist_startswith(self, startletter: str):
        return [artist for artist in self.get_artists() if any([
                    artist.startswith(startletter),
                    artist.startswith(startletter.upper()),
                    artist.startswith(startletter.lower())
                    ])
                ]

    def get_artists(self):
        return [item["artist"] for item in self._client.list("artist") if item["artist"]]

    def get_albums_of_artist(self, artist: str) -> List[str]:
        albums_query_result = [l['album'] for l in self._client.list('album', 'albumartist', artist, 'group', 'date')]
        if albums_query_result:
            return albums_query_result[0]
        return [""]

    def get_track_of_album_of_artist(self, artist: str, album: str) -> Optional[List[str]]:
        return [l["title"] for l in self._client.list('title', 'artist', artist, 'album', album, 'group', 'track')]

    def get_tracks_of_artist(self, artist: str) -> List[str]:
        ...

    def play_track(self):
        ...

    def stats(self) -> Stats:
        return Stats.from_client(self._client)

    def status(self) -> Status:
        return Status.from_client(self._client)
