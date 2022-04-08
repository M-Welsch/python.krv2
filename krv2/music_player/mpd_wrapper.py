from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import List, Optional, Type, Union

from mpd import ConnectionError, MPDClient

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
    def from_cfg(cls, cfg_mpd: dict) -> ConnectionParams:
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
    def from_client(cls, client: MPDClient) -> Stats:
        stats = client.stats()
        return cls(
            uptime=int(stats["uptime"]),
            playtime=int(stats["playtime"]),
            artists=int(stats["artists"]),
            albums=int(stats["albums"]),
            songs=int(stats["songs"]),
            db_playtime=int(stats["db_playtime"]),
            db_update=int(stats["db_update"]),
        )


@dataclass
class Status:
    volume: int
    repeat: int
    random: int
    single: int
    consume: int
    playlist: int
    playlistlength: int
    mixrampdb: float
    state: str

    @classmethod
    def from_client(cls, client: MPDClient) -> Status:
        status = client.status()
        return cls(
            volume=int(status["volume"]),
            repeat=int(status["repeat"]),
            random=int(status["random"]),
            single=int(status["single"]),
            consume=int(status["consume"]),
            playlist=int(status["playlist"]),
            playlistlength=int(status["playlistlength"]),
            mixrampdb=float(status["mixrampdb"]),
            state=str(status["state"]),
        )


def setup_client(conn_params: ConnectionParams) -> MPDClient:
    client = MPDClient()
    client.timeout = conn_params.timeout
    return client


class MpdWrapper:
    def __init__(self, cfg_mpd: dict):
        self._conn_params = ConnectionParams.from_cfg(cfg_mpd)
        self._client: MPDClient = setup_client(self._conn_params)

    def __enter__(self) -> MPDClient:
        self.connect()
        return self._client

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        self._client.close()
        self._client.disconnect()

    def connect(self) -> None:
        self._client.connect(host=self._conn_params.host, port=self._conn_params.port)


class Mpd:
    def __init__(self, cfg_mpd: dict):
        self._mpd_wrapper = MpdWrapper(cfg_mpd=cfg_mpd)

    def artist_startswith(self, startletter: str) -> List[str]:
        return [
            artist
            for artist in self.get_artists()
            if any(
                [
                    artist.startswith(startletter),
                    artist.startswith(startletter.upper()),
                    artist.startswith(startletter.lower()),
                ]
            )
        ]

    def get_artists(self) -> List[str]:
        with self._mpd_wrapper as client:
            return [item["artist"] for item in client.list("artist") if item["artist"]]

    def get_albums_of_artist(self, artist: str) -> List[str]:
        with self._mpd_wrapper as client:
            albums_query_result = [l["album"] for l in client.list("album", "albumartist", artist, "group", "date")]
            return self.flatten_list(albums_query_result)

    def get_track_of_album_of_artist(self, artist: str, album: str) -> List[str]:
        with self._mpd_wrapper as client:
            track_titles = [
                t["title"] for t in client.list("title", "artist", artist, "album", album, "group", "track")
            ]
            return self.flatten_list(track_titles)

    @staticmethod
    def flatten_list(query_result: List[Union[Optional[str], List[str]]]) -> List[str]:
        """processes ['res1', ['res2', 'res3']] -> ['res1', 'res2', 'res3']"""
        flat_list: List[str] = []
        if query_result:
            for album in query_result:
                if isinstance(album, list):
                    flat_list.extend(album)
                elif isinstance(album, str):
                    flat_list.append(album)
        return flat_list

    def get_tracks_of_artist(self, artist: str) -> List[str]:
        with self._mpd_wrapper as client:
            return [t["title"] for t in client.list("title", "artist", artist) if t["title"]]

    # Fixme: here it crashes currently
    def add_tracks(self, artist: str, album: Optional[str], track: Optional[str]) -> None:
        with self._mpd_wrapper as client:
            if artist and not album and not track:
                tracks = client.find("artist", artist)
            elif artist and album and not track:
                tracks = client.find("artist", artist, "album", album)
            elif artist and not album and track:
                tracks = client.find("artist", artist, "title", track)
            elif artist and album and track:
                tracks = client.find("artist", artist, "album", album, "title", track)
            client.add([track["file"] for track in tracks])

    def play_track(self) -> None:
        ...

    def stats(self) -> Stats:
        with self._mpd_wrapper as client:
            return Stats.from_client(client)

    def status(self) -> Status:
        with self._mpd_wrapper as client:
            return Status.from_client(client)
