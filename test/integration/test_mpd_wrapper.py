from dataclasses import fields
from typing import Generator

import pytest

from krv2.music_player.mpd_wrapper import Mpd, MpdWrapper


@pytest.fixture
def mpd() -> Generator[Mpd, None, None]:
    mpd = Mpd({"host": "localhost", "port": 6600, "socket": "/var/run/mpd/socket"})
    assert mpd.stats().artists > 0
    assert mpd.stats().albums > 0
    yield mpd


@pytest.fixture
def mpd_wrapper(mpd: Mpd) -> Generator[MpdWrapper, None, None]:
    yield mpd._mpd_wrapper


def test_mpd_connection_buildup(mpd_wrapper: MpdWrapper) -> None:
    with mpd_wrapper:
        pass


def test_stats_retrieval(mpd: Mpd):
    stats = mpd.stats()
    for field in fields(stats):
        assert field.type == "int"


def test_mpd_get_artists(mpd: Mpd) -> None:
    no_artists = mpd.stats().artists
    artists = mpd.get_artists()
    assert isinstance(artists, list)
    assert len(artists) == no_artists


def test_get_albums_of_artists(mpd: Mpd) -> None:
    artist = mpd.get_artists()[0]
    albums = mpd.get_albums_of_artist(artist)
    assert all([isinstance(album, str) for album in albums])


@pytest.mark.skip("takes long and should only be run, if the following test fails")
def test_get_albums_of_all_artists(mpd: Mpd) -> None:
    artists = mpd.get_artists()
    for artist in artists:
        albums = mpd.get_albums_of_artist(artist)
        assert all([isinstance(album, str) for album in albums])


def test_get_track_of_album_of_artist(mpd: Mpd) -> None:
    artists = mpd.get_artists()
    for artist in artists:
        albums = mpd.get_albums_of_artist(artist)
        assert all([isinstance(album, str) for album in albums])
        for album in albums:
            tracks = mpd.get_track_of_album_of_artist(artist=artist, album=album)
            assert all([isinstance(track, str) for track in tracks])
