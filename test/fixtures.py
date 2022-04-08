from typing import Generator

import pytest

from krv2.music_player.mpd_wrapper import Mpd


@pytest.fixture
def mpd() -> Generator[Mpd, None, None]:
    mpd = Mpd({"host": "localhost", "port": 6600, "socket": "/var/run/mpd/socket"})
    assert mpd.stats().artists > 0
    assert mpd.stats().albums > 0
    yield mpd
