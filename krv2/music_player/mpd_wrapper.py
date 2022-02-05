import logging
from typing import Callable

from mpd import MPDClient, ConnectionError

LOG = logging.getLogger(__name__)


def connect(client, port):
    client.connect("localhost", port)


def outer(func):
    def inner(*args, **kwargs):
        try:
            func()
        except ConnectionError:
            connect()
            func()
    return inner

# https://www.geeksforgeeks.org/creating-decorator-inside-a-class-in-python/


class Mpd:
    def __init__(self, cfg_mpd: dict):
        self._client = self.setup_client(cfg_mpd)

    def setup_client(self, cfg_mpd: dict) -> MPDClient:
        client = MPDClient()
        try:
            port = cfg_mpd["port"]
        except KeyError:
            port = 6600
            LOG.warning(f"mpd port is not defined. Defaulting to {port}")
        client.timeout = 10
        connect(client, port)
        return client

    def safe_mpd_op(self, func: Callable):
        try:
            return func()
        except ConnectionError:
            connect(self._client, 6600)  # Fixme: hand over correct port
            return self.safe_mpd_op(func)

    def _get_artist_query(self):
        return [item["artist"] for item in self._client.list("artist")]

    def get_artists(self):
        return self.safe_mpd_op(self._get_artist_query)

    def get_albums_of_artist(self, artist):
        return self._client.list(...)

