from pathlib import Path
from test.glob_fixtures import db

from krv2.music_collection.database import Database, mc


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
    album_names = db.get_albums_of_artist_by_name("artist0")
    assert isinstance(album_names, list)
    for artist_name in album_names:
        assert isinstance(artist_name, mc.Album)


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
