from typing import List

import mishmash.orm.core as mc
import sqlalchemy.orm.session

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, Numeric, Table, Text, create_engine
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import relationship, sessionmaker, session
from sqlalchemy.ext.declarative import declarative_base


class Database:
    def __init__(self):
        engine = create_engine("sqlite:///mishmash.db", echo=True)
        # Base = mc.Base  # probably unnecessary

        self._session: sqlalchemy.orm.session.Session = sessionmaker(bind=engine)()

    @property
    def session(self) -> sqlalchemy.orm.session.Session:
        return self._session

    def load_artist_names(self) -> List[str]:
        return [art_tuple[0] for art_tuple in self._session.query(mc.Artist.name).order_by(mc.Artist.name).all() if art_tuple]
