from __future__ import annotations  # PEP 585

import os, os.path

from ..const import TMDB_MOVIES_ROOT
from .movie import TmdbMovie


class TmdbMovies:
    def __init__(self):
        pass

    def all_ids(self) -> list[int]:
        def parse(fn: str) -> int | None:
            try:
                return int(os.path.splitext(fn)[0])
            except ValueError:
                return None

        return list(filter(None, map(parse, os.listdir(TMDB_MOVIES_ROOT))))

    def all_persons(self) -> set[int]:
        rez: set = set()
        for mid in self.all_ids():
            m = TmdbMovie(mid)
            d = m.load_data()
            assert d
            for k in ["cast", "crew"]:
                for p in d["credits"][k]:
                    rez.add(p["id"])
        return rez
