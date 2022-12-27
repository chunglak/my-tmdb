from __future__ import annotations  # PEP 585

import datetime
import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import TmdbDb
    from .tmdb import TmdbManager


@dataclass
class TmdbPerson:
    pid: int
    data: dict

    @classmethod
    def from_tmdb(cls, pid: int, tm: TmdbManager) -> TmdbPerson | None:
        try:
            data = {
                "retrieved_dt": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(),
                "details": tm.get_person_details(pid=pid),
                "movie_credits": tm.get_person_movie_credits(pid=pid),
                "tv_credits": tm.get_person_tv_credits(pid=pid),
                "external_ids": tm.get_person_external_ids(pid=pid),
            }
        except:  # pylint: disable=bare-except
            traceback.print_exc()  # to stderr
            return None
        return TmdbPerson(pid=pid, data=data)

    @classmethod
    def from_db(cls, pid: int, db: TmdbDb) -> TmdbPerson | None:
        return db.load_person(pid=pid)

    @classmethod
    def from_db_or_tmdb(
        cls, pid: int, db: TmdbDb, tm: TmdbManager
    ) -> TmdbPerson | None:
        if person := cls.from_db(pid=pid, db=db):
            return person
        else:
            person = cls.from_tmdb(pid=pid, tm=tm)
            if person:
                db.save_person(person)
            return person

    def __str__(self):
        s = self.name
        bdy = self.birthday[:4]
        if dd := self.deathday:
            s += f" ({bdy}–{dd[:4]})"
        else:
            s += f" (b. {bdy})"
        return s

    @property
    def details(self) -> dict:
        return self.data["details"]

    @property
    def name(self) -> str:
        return self.details["name"]

    @property
    def birthday(self) -> str:
        return self.details["birthday"]

    @property
    def deathday(self) -> str:
        return self.details["deathday"]
