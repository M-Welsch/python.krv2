import sys

import logging

import pytest

from krv2.music_collection.database import Database, mc
from test.mockups import create_fake_db_entries


def pytest_configure():
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(filename="test_logging_current.log")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(name)s: %(message)s',
        datefmt='%m.%d.%Y %H:%M:%S',
        handlers=[stdout_handler, file_handler]
    )


@pytest.fixture
def db():
    datab = Database({"path": ":memory:"})
    mc.Base.metadata.create_all(datab._engine)
    create_fake_db_entries(datab.session, amount_artists=5, albums_per_artist=5, tracks_per_album=5)
    yield datab
