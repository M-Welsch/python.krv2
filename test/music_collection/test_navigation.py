from faker import Faker
import pytest
from pytest_mock import MockFixture

import krv2.music_collection
from krv2.music_collection.navigation import PREPENDED_COMMANDS, CommandElement, DatabaseElement, Navigation, Content


@pytest.fixture
def nav():
    class Database:
        @staticmethod
        def get_all_artist_names():
            return []
    db = Database()
    yield Navigation({}, db)


def test_load_artists(mocker: MockFixture) -> None:
    fake = Faker()
    length_artist_list: int = 5

    def load_artist_names():
        return [fake.name() for i in range(length_artist_list)]

    artists = Navigation._load_artists(load_artist_names)
    assert artists.size == length_artist_list + len(PREPENDED_COMMANDS)
    assert len([element for element in artists.elements if isinstance(element, CommandElement)]) == len(PREPENDED_COMMANDS)
    assert len([element for element in artists.elements if isinstance(element, DatabaseElement)]) == length_artist_list
    for element in artists.elements:
        if isinstance(element, CommandElement):
            assert isinstance(element.cmd, str)
        elif isinstance(element, DatabaseElement):
            assert isinstance(element.name, str)
        else:
            raise
    print(f"\n{artists}")


def test_update_list_slice(nav: Navigation) -> None:
    fake = Faker()
    lentgh_fake_names: int = 10
    fake_names = [fake.name() for i in range(lentgh_fake_names)]
    nav._content = Content(elements=[DatabaseElement(name=fakename) for fakename in fake_names])
    for cursor in range(lentgh_fake_names):
        nav._cursor = cursor
        ls = nav._update_list_slice()
        assert len(list(ls)) == nav._slice_size
        assert cursor in ls


def test_up(nav: Navigation, mocker: MockFixture) -> None:
    fake = Faker()
    lentgh_fake_names: int = 10
    fake_names = [fake.name() for i in range(lentgh_fake_names)]
    nav._content = Content(elements=[DatabaseElement(name=fakename) for fakename in fake_names])

    m_update_list_slice = mocker.patch("krv2.music_collection.Navigation._update_list_slice")
    nav._cursor = initial_cursor = 0
    nav.up()
    assert nav._cursor == initial_cursor + 1
    assert m_update_list_slice.called_once

    m_update_list_slice.reset_mock()
    nav._cursor = last_cursor_pos = lentgh_fake_names
    nav.up()
    assert nav._cursor == last_cursor_pos
    assert m_update_list_slice.call_count == 0


def test_down(nav: Navigation, mocker: MockFixture) -> None:
    m_update_list_slice = mocker.patch("krv2.music_collection.Navigation._update_list_slice")
    nav._cursor = initial_cursor = 1
    nav.down()
    assert nav._cursor == initial_cursor - 1
    assert m_update_list_slice.called_once

    m_update_list_slice.reset_mock()
    nav.down()
    assert nav._cursor == 0
    assert m_update_list_slice.call_count == 0


