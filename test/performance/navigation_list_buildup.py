from subprocess import run, PIPE
from time import time

from krv2.music_collection import Database, Navigation

TEST_DB_PATH = "test/test_mishmash.db"


def test_db_buildup():
    cmd = f"mishmash -D sqllite:///{TEST_DB_PATH} sync ~/Music"
    begin = time()
    p = run(cmd.split(), stdout=PIPE)
    for line in p.stdout:
        pass
    duration = time() - begin
    print(f"scan of {TEST_DB_PATH} took {duration:.1f} seconds")


def test_list_buildup_speed():
    db = Database({"path": TEST_DB_PATH})
    begin = time()
    nav = Navigation({}, db)
    duration = time() - begin
    print(f"listing all artists of {TEST_DB_PATH} took {duration:.1f} seconds")