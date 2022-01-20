from pathlib import Path
import pytest

from krv2.music_collection import Navigation
from krv2.music_collection.database import Database, mc
from krv2.music_collection.navigation import ContentLayer, DatabaseElement, CommandElement, PREPENDED_COMMANDS
from test.mockups import create_fake_db_entries


@pytest.fixture
def nav():
    db = Database({"path": ":memory:"})
    mc.Base.metadata.create_all(db._engine)
    create_fake_db_entries(db.session, amount_artists=5, albums_per_artist=5, tracks_per_album=5)
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
    for iartist in range(5):
        nav._cursor.index = len(PREPENDED_COMMANDS)
        assert nav._cursor.layer == ContentLayer.artist_list
        nav.into()
        assert nav._cursor.layer == ContentLayer.album_list
        for index, db_element in enumerate(nav._content.db_elements):
            assert isinstance(db_element.db_reference, mc.Album)
            assert db_element.db_reference.artist == nav._cursor.current_artist
        nav.out()
        assert nav._cursor.layer == ContentLayer.artist_list
        nav.down()
        assert nav._cursor.layer == ContentLayer.artist_list