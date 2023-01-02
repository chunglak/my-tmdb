from __future__ import annotations  # PEP 585

import json

from .db import TmdbDb
from .movie import TmdbMovie
from .person import TmdbPerson


def make_tmdb_persons_id_file(fn: str):
    def process(pid: int) -> str:
        p = TmdbPerson.from_db_or_tmdb(pid=pid)
        return f"{p} :: {pid}"

    db = TmdbDb()
    ms = db.all_movie_ids()
    pids: set = set()
    for m in ms:
        mid, js = m
        movie = TmdbMovie(mid=mid, data=json.loads(js))
        pids.union(movie.person_ids())
    with open(fn, "w", encoding="utf8") as fh:
        fh.write("\n".join(map(process, sorted(pids))))
        fh.write("\n")
