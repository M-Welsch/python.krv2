from pathlib import Path
import pytest

from krv2.music_collection import Navigation
from krv2.music_collection.database import Database, mc
from krv2.music_collection.navigation import ContentLayer, DatabaseElement, CommandElement, PREPENDED_COMMANDS
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
    db_elements = [e for e in nav._content.elements if isinstance(e, DatabaseElement)]
    for index, db_element in enumerate(db_elements):
        assert isinstance(db_element.db_reference, mc.Artist)
        assert db_element.name == f"artist{index}"


def test_content_composition(nav: Navigation) -> None:
    db_elements = [e for e in nav._content.elements if isinstance(e, DatabaseElement)]
    cmd_elements = [e for e in nav._content.elements if isinstance(e, CommandElement)]
    assert len(cmd_elements) == len(PREPENDED_COMMANDS)
    assert len(db_elements) == 5


def test_get_artists(nav: Navigation) -> None:
    for i in range(len(PREPENDED_COMMANDS)):
        assert isinstance(nav._content.elements[nav._cursor.index], CommandElement)
        print(nav._cursor.current_pos)
        nav.down()
    for iartist in range(AMOUNT_ARTISTS):
        assert isinstance(nav._content.elements[nav._cursor.index], DatabaseElement)
        assert nav._cursor.layer == ContentLayer.artist_list
        print(nav._cursor.current_pos)
        nav.into()
        assert nav._cursor.layer == ContentLayer.album_list
        for index, db_element in enumerate(nav._content.db_elements):
            assert isinstance(db_element.db_reference, mc.Album)
            assert db_element.db_reference.artist == nav._cursor.current_artist
        print(nav._cursor.current_pos)
        nav.out()
        assert nav._cursor.layer == ContentLayer.artist_list
        print(nav._cursor.current_pos)
        nav.down()
        assert nav._cursor.layer == ContentLayer.artist_list


def test_get_albums(nav: Navigation) -> None:
    ...


def test_traverse_database(nav: Navigation) -> None:
    nav._cursor.goto_first_db_element()
    for iartist in range(AMOUNT_ARTISTS):
        nav.into()
        nav._cursor.goto_first_db_element()
        for ialbum in range(ALBUMS_PER_ARTIST):
            nav.into()
            nav._cursor.goto_first_db_element()
            for itrack in range(TRACKS_PER_ALBUM):
                nav.down()
            nav.out()
            nav.down()
        nav.down()
        nav.out()

