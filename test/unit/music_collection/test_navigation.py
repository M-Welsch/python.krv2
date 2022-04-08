from test.fixtures import mpd  # do not delete
from test.utils import derive_mock_string
from typing import Generator, List

import pytest
from faker import Faker
from pytest_mock import MockFixture

import krv2.music_collection
from krv2.music_collection.navigation import Content, ContentElement, ContentLayer, Navigation
from krv2.music_player.mpd_wrapper import Mpd


@pytest.fixture
def nav(mpd) -> Generator[Navigation, None, None]:
    yield Navigation({}, mpd)


def test_update_list_slice(nav: Navigation) -> None:
    for cursor in range(5):
        nav._cursor.index = cursor
        ls = nav._update_list_slice()
        assert len(list(ls)) == nav._slice_size
        assert cursor in ls


def test_down(nav: Navigation, mocker: MockFixture) -> None:
    m_update_list_slice = mocker.patch(derive_mock_string(krv2.music_collection.Navigation._update_list_slice))
    nav._cursor.index = initial_cursor = 0
    nav._cursor.list_size = len(nav._cursor._content.elements)
    nav.down()
    assert nav._cursor.index == initial_cursor + 1
    assert m_update_list_slice.called_once

    m_update_list_slice.reset_mock()
    nav._cursor.index = nav._cursor.list_size - 2
    nav.down()
    assert nav._cursor.index == nav._cursor.list_size - 1
    assert m_update_list_slice.call_count == 1

    m_update_list_slice.reset_mock()
    nav.down()
    assert nav._cursor.index == nav._cursor.list_size - 1
    assert m_update_list_slice.call_count == 0


def test_up(nav: Navigation, mocker: MockFixture) -> None:
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
    m_build_content_list = mocker.patch(derive_mock_string(krv2.music_collection.navigation.Cursor.build_content_list))
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
    m_build_content_list = mocker.patch(derive_mock_string(krv2.music_collection.navigation.Cursor.build_content_list))
    m_derivate_cursor_index = mocker.patch(
        derive_mock_string(krv2.music_collection.navigation.Navigation._derive_cursor_index)
    )
    nav.down()  # first artist doesn't have albums
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
    assert isinstance(nav._cursor.current, ContentElement)
    nav.into()
    nav.out()
    assert nav._cursor.index == cursor_index_pre_test


def test_derive_cursor_index_multiple(nav: Navigation) -> None:
    for artist in nav._mpd.get_artists():
        cursor_index_pre_test = nav._cursor.index
        layer_pre_test = nav.layer
        assert isinstance(nav._cursor.current, ContentElement)
        nav.into()
        assert not layer_pre_test == nav.layer
        nav.out()
        assert nav.layer == layer_pre_test
        assert nav._cursor.index == cursor_index_pre_test
        nav.down()
