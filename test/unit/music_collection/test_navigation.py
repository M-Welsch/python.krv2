from test.utils import derive_mock_string
from typing import List

import pytest
from faker import Faker
from pytest_mock import MockFixture

import krv2.music_collection
from krv2.music_collection.database import mc
from test.glob_fixtures import db, AMOUNT_FAKE_ARTISTS
from krv2.music_collection.navigation import Content, ContentLayer, Navigation


class Artist:
    def __init__(self, name, db_reference):
        self.name: str = name
        self.db_reference: int = db_reference


@pytest.fixture
def nav(db):
    yield Navigation({}, db)


@pytest.fixture
def nav_w_fake_content(nav):
    fake = Faker()
    lengh_fake_names: int = 2
    fake_names = [fake.name() for i in range(lengh_fake_names)]
    nav._cursor._content = Content(
        content_elements=[fakename for fakename in fake_names]
    )
    yield nav


def test_load_artists(nav: Navigation, mocker: MockFixture) -> None:
    fake = Faker()
    length_artist_list: int = 5

    def get_all_artists() -> List[Artist]:
        return [Artist(fake.name(), i) for i in range(length_artist_list)]

    nav._db.get_all_artists = get_all_artists
    artists = nav._cursor._load_artists()
    assert len(artists) == length_artist_list
    assert len([element for element in artists]) == length_artist_list
    for artist in artists:
        # assert isinstance(artist, mc.Artist)  # cannot
        assert isinstance(artist.name, str)
    print(artists)


def test_update_list_slice(nav: Navigation) -> None:
    # fake = Faker()
    # lentgh_fake_names: int = 10
    # fake_names = [fake.name() for i in range(lentgh_fake_names)]
    # nav._content = Content(
    #     content_elements=[ContentElement(caption=fakename, db_reference=0) for fakename in fake_names])
    for cursor in range(5):
        nav._cursor.index = cursor
        ls = nav._update_list_slice()
        assert len(list(ls)) == nav._slice_size
        assert cursor in ls


def test_down(nav: Navigation, mocker: MockFixture) -> None:
    m_update_list_slice = mocker.patch(derive_mock_string(krv2.music_collection.Navigation._update_list_slice))
    current_test_cursor = 0
    assert nav._cursor.index == current_test_cursor

    while not nav._cursor.current_artist == nav._cursor.content.elements[-1]:
        nav.down()
        current_test_cursor += 1
        assert nav._cursor.index == current_test_cursor
        assert m_update_list_slice.called_once
        m_update_list_slice.reset_mock()

    push_cursor_down_below_end = 5
    for i in range(push_cursor_down_below_end):
        nav.down()
        assert nav._cursor.current == nav._cursor.content.elements[-1]
        assert nav._cursor.index == nav._cursor.list_size - 1
        assert m_update_list_slice.call_count == 0


def test_up(nav: Navigation, mocker: MockFixture) -> None:
    # nav = nav_w_fake_content  # just for convenience
    m_update_list_slice = mocker.patch("krv2.music_collection.Navigation._update_list_slice")
    nav._cursor.index = initial_cursor = 1
    nav.up()
    assert nav._cursor.index == initial_cursor - 1
    assert m_update_list_slice.called_once

    m_update_list_slice.reset_mock()
    nav.up()
    assert nav._cursor.index == 0
    assert m_update_list_slice.call_count == 0


def test_into(nav: Navigation, mocker: MockFixture) -> None:
    m_build_content_list = mocker.patch(derive_mock_string(krv2.music_collection.navigation.Cursor.refresh_content))
    m_repr = mocker.patch(derive_mock_string(krv2.music_collection.navigation.Cursor.__repr__), return_value="mmock")
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
    m_build_content_list = mocker.patch(derive_mock_string(krv2.music_collection.navigation.Cursor.refresh_content))
    m_derivate_cursor_index = mocker.patch(
        derive_mock_string(krv2.music_collection.navigation.Navigation._derive_cursor_index)
    )
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


def test_derive_cursor_index(nav: Navigation) -> None:
    cursor_index_pre_test = nav._cursor.index
    nav.into()
    nav.out()
    assert nav._cursor.index == cursor_index_pre_test
