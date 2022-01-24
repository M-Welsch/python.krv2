from pathlib import Path
from typing import List

import mishmash.orm.core as mc
from mishmash.orm import Album

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import logging

LOG = logging.getLogger(__name__)


class Database:
    def __init__(self, cfg_db: dict, verbose: bool = False):
        print("cfg_dict <<<<<<<<<<<<<<<<<<<<<<<")
        print(cfg_db)
        connect_str = f"sqlite:///{cfg_db['path']}"
        LOG.info(f"connecting to database with: {connect_str}")
        self._engine = create_engine(connect_str, echo=verbose)
        self._session: Session = sessionmaker(bind=self._engine)()
        self.create_missing_tables(cfg_db.get("create_tables_if_nonexistent", True))

    def create_missing_tables(self, create_tables_if_nonexistent: bool):
        if create_tables_if_nonexistent:
            mc.Base.metadata.create_all(self._engine)

    @property
    def session(self) -> Session:
        return self._session

    def get_all_artists(self) -> List[mc.Artist]:
        return self._session.query(mc.Artist).order_by(mc.Artist.name).all()

    def get_all_artist_names(self) -> List[str]:
        return [artist.name[0] for artist in self.get_all_artists() if artist]

    def get_artist_by_name(self, name: str) -> mc.Artist:
        return self._session.query(mc.Artist).filter(mc.Artist.name == name).first()

    @staticmethod
    def get_albums_of_artist(artist: mc.Artist) -> List[mc.Album]:
        return artist.albums

    def get_albums_of_artist_by_name(self, artist_name: str) -> List[mc.Artist]:
        artist = self._session.query(mc.Artist).filter(mc.Artist.name == artist_name).first()
        return [album for album in artist.albums]

    def get_tracks_of_album_by_name(self, artist_name: str, album_title: str) -> List[mc.Track]:
        artist = self.get_artist_by_name(artist_name)
        albums = self.get_albums_of_artist(artist)
        if albums:
            album: Album
            for album in albums:
                if album.title == album_title:
                    break
            return album.tracks
        else:
            return []

    def get_tracks_of_album(self, artist: mc.Artist, album: mc.Album) -> List[mc.Track]:
        return self.get_tracks_of_album_by_name(artist_name=artist.name, album_title=album.title)

    @staticmethod
    def get_track_file_location(track: mc.Track) -> Path:
        return Path(track.path)
