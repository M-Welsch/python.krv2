from pathlib import Path
from typing import List

import mishmash.orm.core as mc

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, Numeric, Table, Text, create_engine
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base


class Database:
    def __init__(self, cfg_db: dict):
        self._session: Session = self.get_session(cfg_db["path"])

    @staticmethod
    def get_session(db_path: str) -> Session:
        engine = create_engine(f"sqlite:///{db_path}", echo=True)
        return sessionmaker(bind=engine)()

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
    def get_albums_of_artist(artist) -> List[mc.Album]:
        return artist.albums

    def get_albums_of_artist_by_name(self, artist_name: str) -> List[str]:
        artist = self._session.query(mc.Artist).filter(mc.Artist.name == artist_name).first()
        return [album.title for album in artist.albums]

    def get_tracks_of_album_by_name(self, artist_name: str, album_title: str) -> List[mc.Track]:
        artist = self.get_artist_by_name(artist_name)
        albums = self.get_albums_of_artist(artist)
        if albums:
            for album in albums:
                if album.title == album_title:
                    break
            return album.tracks
        else:
            return []

    @staticmethod
    def get_track_file_location(track: mc.Track) -> Path:
        return Path(track.path)
