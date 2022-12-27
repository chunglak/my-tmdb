from __future__ import annotations  # PEP 585

import datetime
import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import TmdbDb
    from .tmdb import TmdbManager


@dataclass
class TmdbMovie:
    mid: int
    data: dict

    @classmethod
    def from_tmdb(cls, mid: int, tm: TmdbManager) -> TmdbMovie | None:
        try:
            data = {
                "retrieved_dt": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(),
                "details": tm.get_movie_details(mid=mid),
                "credits": tm.get_movie_credits(mid=mid),
                "external_ids": tm.get_movie_external_ids(mid=mid),
                "keywords": tm.get_movie_keywords(mid=mid),
            }
        except:  # pylint: disable=bare-except
            traceback.print_exc()  # to stderr
            return None
        return TmdbMovie(mid=mid, data=data)

    @classmethod
    def from_db(cls, mid: int, db: TmdbDb) -> TmdbMovie | None:
        return db.load_movie(mid=mid)

    @classmethod
    def from_db_or_tmdb(
        cls, mid: int, db: TmdbDb, tm: TmdbManager
    ) -> TmdbMovie | None:
        if movie := cls.from_db(mid=mid, db=db):
            return movie
        else:
            movie = cls.from_tmdb(mid=mid, tm=tm)
            if movie:
                db.save_movie(movie)
            return movie

    def __str__(self):
        t, ot = self.title, self.original_title
        s = t
        if ot and ot != t:
            s += f" [{ot}]"
        s += f" ({self.year})"
        return s

    @property
    def details(self) -> dict:
        return self.data["details"]

    @property
    def title(self) -> str:
        return self.details["title"]

    @property
    def original_title(self) -> str:
        return self.details["original_title"]

    @property
    def year(self) -> int:
        return int(self.details["release_date"][:4])
