from typing import List

from faker import Faker
import pytest
from pytest_mock import MockFixture

import krv2.music_collection
from krv2.music_collection.navigation import PREPENDED_COMMANDS, CommandElement, DatabaseElement, Navigation, Content, \
    ContentLayer


class Artist:
    def __init__(self, name, db_reference):
        self.name: str = name
        self.db_reference: int = db_reference


@pytest.fixture
def nav():
    class Database:
        @staticmethod
        def get_all_artists():
            return []
    db = Database()
    yield Navigation({}, db)


def test_load_artists(nav: Navigation, mocker: MockFixture) -> None:
    fake = Faker()
    length_artist_list: int = 5

    def get_all_artists() -> List[Artist]:
        return [Artist(fake.name(), i) for i in range(length_artist_list)]

    nav._db.get_all_artists = get_all_artists
    artists = nav._load_artists()
    assert len(artists) == length_artist_list
    assert len([element for element in artists if isinstance(element, DatabaseElement)]) == length_artist_list
    for artist in artists:
        assert isinstance(artist, DatabaseElement)
        assert isinstance(artist.name, str)
        # assert isinstance(artist.db_reference, mc.Artist)  # cannot check for that right now
    print(artists)


def test_update_list_slice(nav: Navigation) -> None:
    fake = Faker()
    lentgh_fake_names: int = 10
    fake_names = [fake.name() for i in range(lentgh_fake_names)]
    nav._content = Content(database_elements=[DatabaseElement(caption=fakename, db_reference=0) for fakename in fake_names])
    for cursor in range(lentgh_fake_names):
        nav._cursor.index = cursor
        ls = nav._update_list_slice()
        assert len(list(ls)) == nav._slice_size
        assert cursor in ls


def test_up(nav: Navigation, mocker: MockFixture) -> None:
    fake = Faker()
    lentgh_fake_names: int = 2
    fake_names = [fake.name() for i in range(lentgh_fake_names)]
    nav._content = Content(database_elements=[DatabaseElement(caption=fakename, db_reference=0) for fakename in fake_names])

    m_update_list_slice = mocker.patch("krv2.music_collection.Navigation._update_list_slice")
    nav._cursor.index = initial_cursor = 0
    nav._cursor.list_size = lentgh_fake_names
    nav.up()
    assert nav._cursor.index == initial_cursor + 1
    assert m_update_list_slice.called_once

    m_update_list_slice.reset_mock()
    nav.up()
    assert nav._cursor.index == nav._cursor.list_size - 1
    assert m_update_list_slice.call_count == 0


def test_down(nav: Navigation, mocker: MockFixture) -> None:
    m_update_list_slice = mocker.patch("krv2.music_collection.Navigation._update_list_slice")
    nav._cursor.index = initial_cursor = 1
    nav.down()
    assert nav._cursor.index == initial_cursor - 1
    assert m_update_list_slice.called_once

    m_update_list_slice.reset_mock()
    nav.down()
    assert nav._cursor.index == 0
    assert m_update_list_slice.call_count == 0


def test_into(nav: Navigation, mocker: MockFixture) -> None:
    m_build_content_list = mocker.patch("krv2.music_collection.Navigation.build_content_list")
    assert nav._cursor.layer == ContentLayer.artist_list
    nav.into()
    assert nav._cursor.layer == ContentLayer.album_list
    assert m_build_content_list.call_count == 1
    assert nav._cursor.index == 0
    # assert albums of selected artists are now in content?
    m_build_content_list.reset_mock()

    nav.into()
    assert nav._cursor.layer == ContentLayer.track_list
    assert m_build_content_list.call_count == 1
    assert nav._cursor.index == 0
    m_build_content_list.reset_mock()

    nav.into()
    assert m_build_content_list.call_count == 0


def test_out(nav: Navigation, mocker: MockFixture) -> None:
    m_build_content_list = mocker.patch("krv2.music_collection.Navigation.build_content_list")
    m_derivate_cursor_index = mocker.patch("krv2.music_collection.Navigation._derivate_cursor_index")
    nav._cursor.layer = ContentLayer.track_list

    nav.out()
    assert nav._cursor.layer == ContentLayer.album_list
    assert m_build_content_list.call_count == 1
    assert m_derivate_cursor_index.call_count == 1
    m_build_content_list.reset_mock()
    m_derivate_cursor_index.reset_mock()

    nav.out()
    assert nav._cursor.layer == ContentLayer.artist_list
    assert m_build_content_list.call_count == 1
    assert m_derivate_cursor_index.call_count == 1
    m_build_content_list.reset_mock()
    m_derivate_cursor_index.reset_mock()

    nav.out()
    assert m_build_content_list.call_count == 0
    assert m_derivate_cursor_index.call_count == 0


def test_derivate_cursor_index(nav: Navigation) -> None:
    ...
