from pathlib import Path
import pytest

from krv2.music_collection import Navigation
from krv2.music_collection.database import Database, mc
from krv2.music_collection.navigation import ContentLayer, ContentElement
from test.mockups import create_fake_db_entries


AMOUNT_ARTISTS = 5
ALBUMS_PER_ARTIST = 5
TRACKS_PER_ALBUM = 5


@pytest.fixture
def nav():
    db = Database({"path": ":memory:"})
    mc.Base.metadata.create_all(db._engine)
    create_fake_db_entries(db.session, amount_artists=AMOUNT_ARTISTS,
                           albums_per_artist=ALBUMS_PER_ARTIST, tracks_per_album=TRACKS_PER_ALBUM)
    yield Navigation({}, db)


def test_initial_stage(nav: Navigation) -> None:
    assert nav._cursor.index == 0
    assert nav._cursor.layer == ContentLayer.artist_list
    assert nav._slice_range == range(nav._slice_size)
    db_elements = [e for e in nav._cursor._content.elements if isinstance(e, ContentElement)]
    for index, db_element in enumerate(db_elements):
        assert isinstance(db_element.db_reference, mc.Artist)
        assert db_element.name == f"artist{index}"


def test_content_composition(nav: Navigation) -> None:
    db_elements = [e for e in nav._cursor._content.elements if isinstance(e, ContentElement)]
    assert len(db_elements) == 5


def test_get_artists(nav: Navigation) -> None:
    for iartist in range(AMOUNT_ARTISTS):
        assert isinstance(nav._cursor._content.elements[nav._cursor.index], ContentElement)
        assert nav._cursor.layer == ContentLayer.artist_list
        print(nav._cursor)
        nav.into()
        assert nav._cursor.layer == ContentLayer.album_list
        for index, db_element in enumerate(nav._cursor._content.elements):
            assert isinstance(db_element.db_reference, mc.Album)
            assert db_element.db_reference.artist == nav._cursor.current_artist
        print(nav._cursor)
        nav.out()
        assert nav._cursor.layer == ContentLayer.artist_list
        print(nav._cursor)
        nav.down()
        assert nav._cursor.layer == ContentLayer.artist_list


def test_get_albums(nav: Navigation) -> None:
    ...


def test_traverse_database(nav: Navigation) -> None:
    for iartist in range(AMOUNT_ARTISTS):
        print(nav._cursor)
        nav.into()
        for ialbum in range(ALBUMS_PER_ARTIST):
            print(nav._cursor)
            nav.into()
            for itrack in range(TRACKS_PER_ALBUM):
                print(nav._cursor)
                nav.down()
            print(nav._cursor)
            nav.out()
            print(nav._cursor)
            nav.down()
        print(nav._cursor)
        nav.down()
        print(nav._cursor)
        nav.out()

