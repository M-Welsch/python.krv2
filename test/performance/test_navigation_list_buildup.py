from pathlib import Path
from subprocess import PIPE, run
from time import time

import pytest

from krv2.music_collection import Database, Navigation

TEST_DB_PATH = Path.cwd() / "test/test_mishmash.db"
MUSIC_LIB_DIR = Path.cwd().parent / "Music"


@pytest.mark.performance
def test_db_buildup():
    cmd = f"mishmash -D sqlite:///{TEST_DB_PATH} sync {MUSIC_LIB_DIR}"
    begin = time()
    p = run(cmd.split(), stdout=PIPE)
    duration = time() - begin
    print(f"scan of {TEST_DB_PATH} took {duration:.1f} seconds")


# Results on raspi3 (same Music collection snapshot)
# wtest_db_buildup: 44.3s
# mishmash solo: 39.5s


@pytest.mark.performance
def test_list_buildup_speed():
    db = Database({"path": TEST_DB_PATH})
    begin = time()
    nav = Navigation({}, db)
    duration = time() - begin
    print(f"listing all artists of {TEST_DB_PATH} took {duration:.1f} seconds")


# 0.1s for 1039 tracks (about 6 Artists)
