from dataclasses import fields

import pytest

from krv2.music_player.mpd_wrapper import Mpd


@pytest.fixture
def mpd_wrapper():
    yield Mpd({})


def test_mpd_connection_buildup(mpd_wrapper: Mpd) -> None:
    with mpd_wrapper as m:
        pass


def test_stats_retrieval(mpd_wrapper: Mpd):
    with mpd_wrapper as m:
        stats = m.stats()
    for field in fields(stats):
        assert field.type == int


def test_mpd_get_artists(mpd_wrapper: Mpd) -> None:
    with mpd_wrapper as m:
        no_artists = m.stats().artists
        artists = m.get_artists()
    assert isinstance(artists, list)
    assert len(artists) == no_artists
