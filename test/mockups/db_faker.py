from datetime import datetime

from sqlalchemy.orm import Session

from krv2.music_collection.database import mc


def create_fake_db_entries(session: Session, amount_artists: int, albums_per_artist: int, tracks_per_album: int) -> None:
    lib = mc.Library(name="myownlibrary")
    fake_artists = [mc.Artist(
        name=f"artist{i}", sort_name=f"artist{i}", date_added=datetime.now(), library=lib
    ) for i in range(amount_artists)]
    for fake_artist in fake_artists:
        fake_albums = [mc.Album(
            title=f"album{i}", date_added=datetime.now(), artist=fake_artist, library=lib
        ) for i in range(albums_per_artist)]
        for fake_album in fake_albums:
            fake_tracks = [mc.Track(
                path=f"{fake_artist}/{fake_album}/{i}.mp3", size_bytes=(i+1), ctime=datetime.now(), mtime=datetime.now(), date_added=datetime.now(),
                time_secs=(i+1), title=f"Track{i}", metadata_format="IID3v2.3", artist=fake_artist, album=fake_album, library=lib
            )for i in range(tracks_per_album)]
            session.add_all(fake_tracks)
        session.add_all(fake_albums)
    session.add_all(fake_artists)
    session.commit()
