from pathlib import Path
import pytest

from krv2.music_collection.database import Database, mc
from test.mockups import create_fake_db_entries


@pytest.fixture
def db():
    datab = Database({"path": ":memory:"})
    mc.Base.metadata.create_all(datab._engine)
    create_fake_db_entries(datab.session, amount_artists=5, albums_per_artist=5, tracks_per_album=5)
    yield datab


def test_get_all_artists(db: Database) -> None:
    artists = db.get_all_artists()
    assert isinstance(artists, list)
    for artist_name in artists:
        assert isinstance(artist_name, mc.Artist)


def test_get_artist_names(db: Database) -> None:
    artist_names = db.get_all_artist_names()
    assert isinstance(artist_names, list)
    for artist_name in artist_names:
        assert isinstance(artist_name, str)


def test_get_albums_of_artist(db: Database) -> None:
    album_names = db.get_albums_of_artist_by_name('artist0')
    assert isinstance(album_names, list)
    for artist_name in album_names:
        assert isinstance(artist_name, str)


def test_get_tracks_of_album_by_name(db: Database) -> None:
    tracks = db.get_tracks_of_album_by_name(artist_name="artist0", album_title="album0")
    assert isinstance(tracks, list)
    for artist_name in tracks:
        assert isinstance(artist_name, mc.Track)


def test_get_track_file_location(db: Database) -> None:
    tracks = db.get_tracks_of_album_by_name(artist_name="artist0", album_title="album0")
    for track in tracks:
        filepath = db.get_track_file_location(track)
        assert isinstance(filepath, Path)
        assert filepath.exists()


