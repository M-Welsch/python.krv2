from subprocess import run

from krv2.music_collection import Database, Navigation

TEST_DB_PATH = "test/test_mishmash.db"


def test_db_buildup():
    cmd = f"mishmash -D sqllite:///{TEST_DB_PATH} sync ~/Music"
    run(cmd.split())


def test_list_buildup_speed():
    db = Database({"path": TEST_DB_PATH})
    nav = Navigation({}, db)
