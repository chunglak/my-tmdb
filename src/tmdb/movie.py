from __future__ import annotations  # PEP 585

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import TmdbDb
    from .tmdb import TmdbManager

from .errors import TmdbNotFoundError


@dataclass
class TmdbMovie:
    mid: int
    data: dict

    @classmethod
    def from_tmdb(
        cls, mid: int, tm: TmdbManager | None = None
    ) -> TmdbMovie | None:
        from .tmdb import TmdbManager  # pylint: disable=import-outside-toplevel

        if not tm:
            tm = TmdbManager()
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
        except TmdbNotFoundError:
            return None
        return TmdbMovie(mid=mid, data=data)

    @classmethod
    def from_db(cls, mid: int, db: TmdbDb | None = None) -> TmdbMovie | None:
        from .db import TmdbDb  # pylint: disable=import-outside-toplevel

        if not db:
            db = TmdbDb()
        return db.load_movie(mid=mid)

    @classmethod
    def from_db_or_tmdb(
        cls, mid: int, db: TmdbDb | None = None, tm: TmdbManager | None = None
    ) -> TmdbMovie | None:
        from .db import TmdbDb  # pylint: disable=import-outside-toplevel
        from .tmdb import TmdbManager  # pylint: disable=import-outside-toplevel

        if not db:
            db = TmdbDb()
        if movie := cls.from_db(mid=mid, db=db):
            return movie
        else:
            if not tm:
                tm = TmdbManager()
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
        if rd := self.details["release_date"]:
            return int(rd[:4])
        else:
            return 0

    @property
    def url(self) -> str:
        return f"https://www.themoviedb.org/movie/{self.mid}"

    @property
    def imdb_url(self) -> str | None:
        if iid := self.details.get("imdb_id"):
            return f"https://www.imdb.com/title/{iid}"
        else:
            return None

    def person_ids(self) -> set[int]:
        pids = set()
        cs = self.data["credits"]
        for k in ["cast", "crew"]:
            for rec in cs[k]:
                pids.add(rec["id"])
        return pids

    def infos(self) -> dict:
        def crew_find(jobs: list[str]):
            pids = []
            rez = []
            for rec in crew:
                pid = rec["id"]
                if pid in pids:
                    continue
                if rec["job"] in jobs:
                    rez.append({"name": rec["name"], "id": pid})
                    pids.append(pid)
            return rez

        cast = self.data["credits"]["cast"]
        cast_rec = [
            {
                "character": rec["character"],
                "actor": rec["name"],
                "pid": rec["id"],
            }
            for rec in cast
        ]

        crew = self.data["credits"]["crew"]
        crew_rec = {
            "director": crew_find(["Director"]),
            "writer": crew_find(["Screenplay", "Writer", "Novel"]),
            "composer": crew_find(["Original Music Composer", "Music"]),
        }

        details = self.data["details"]
        otitle: str | None = self.original_title
        if otitle == self.title:
            otitle = None
        rez = {
            "id": self.mid,
            "title": self.title,
            "original_title": otitle,
            "year": self.year,
            "runtime": details["runtime"],
            "original_language": details["original_language"],
            "languages": [
                rec["english_name"] for rec in details["spoken_languages"]
            ],
            "overview": details["overview"],
            "genres": [rec["name"] for rec in details["genres"]],
            "cast": cast_rec,
            "crew": crew_rec,
            "countries": [
                rec["name"] for rec in details["production_countries"]
            ],
            "rating": details["vote_average"],
        }
        if iid := self.data["external_ids"].get("imdb_id"):
            rez["imdb_id"] = iid
        if wid := self.data["external_ids"].get("wikidata_id"):
            rez["wikidata_id"] = wid
        return rez
