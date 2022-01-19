from faker import Faker
import pytest
from pytest_mock import MockFixture

from krv2.music_collection.navigation import PREPENDED_COMMANDS, CommandElement, DatabaseElement, Navigation


@pytest.fixture
def nav(mocker: MockFixture):
    class Database:
        @staticmethod
        def load_artist_names():
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
    ...