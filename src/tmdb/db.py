from __future__ import annotations  # PEP 585

import json
import logging
import os.path
import sqlite3

from .const import TMDB_DB_FILE
from .movie import TmdbMovie
from .person import TmdbPerson


class TmdbDb:
    def __init__(self, db_fn: str | None = None):
        self.db_fn = db_fn if db_fn else TMDB_DB_FILE
        if not os.path.isfile(self.db_fn):
            self.create_db()

    def create_db(self):
        with sqlite3.connect(self.db_fn) as conn:
            conn.execute(
                """
                create table movies(
                id           int primary key unique,
                data         text
                )
                """
            )
            conn.execute(
                """
                create table persons(
                id           int primary key unique,
                data         text
                )
                """
            )
        logging.info("Created database file %s", self.db_fn)
        return True

    def save_movie(self, movie: TmdbMovie) -> int:
        with sqlite3.connect(self.db_fn) as conn:
            r = conn.execute(
                "insert or replace into movies(id,data) values (?,?)",
                (movie.mid, json.dumps(movie.data)),
            )
            logging.info("Saved %s to db", movie)
            return r.rowcount

    def load_movie(self, mid: int) -> TmdbMovie | None:
        with sqlite3.connect(self.db_fn) as conn:
            r = conn.execute(
                "select data from movies where id=?", (mid,)
            ).fetchone()
            if r:
                return TmdbMovie(mid=mid, data=json.loads(r[0]))
            else:
                return None

    def save_person(self, person: TmdbPerson) -> int:
        with sqlite3.connect(self.db_fn) as conn:
            r = conn.execute(
                "insert or replace into persons(id,data) values (?,?)",
                (person.pid, json.dumps(person.data)),
            )
            logging.info("Saved %s to db", person)
            return r.rowcount

    def load_person(self, pid: int) -> TmdbPerson | None:
        with sqlite3.connect(self.db_fn) as conn:
            r = conn.execute(
                "select data from persons where id=?", (pid,)
            ).fetchone()
            if r:
                return TmdbPerson(pid=pid, data=json.loads(r[0]))
            else:
                return None
