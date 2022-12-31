from __future__ import annotations  # PEP 585

import datetime
import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta

if TYPE_CHECKING:
    from .db import TmdbDb
    from .tmdb import TmdbManager


@dataclass
class TmdbPerson:
    pid: int
    data: dict

    @classmethod
    def from_tmdb(
        cls, pid: int, tm: TmdbManager | None = None
    ) -> TmdbPerson | None:
        from .tmdb import TmdbManager  # pylint: disable=import-outside-toplevel

        if not tm:
            tm = TmdbManager()
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
    def from_db(cls, pid: int, db: TmdbDb | None = None) -> TmdbPerson | None:
        from .db import TmdbDb  # pylint: disable=import-outside-toplevel

        if not db:
            db = TmdbDb()
        return db.load_person(pid=pid)

    @classmethod
    def from_db_or_tmdb(
        cls, pid: int, db: TmdbDb | None = None, tm: TmdbManager | None = None
    ) -> TmdbPerson | None:
        from .db import TmdbDb  # pylint: disable=import-outside-toplevel
        from .tmdb import TmdbManager  # pylint: disable=import-outside-toplevel

        if not db:
            db = TmdbDb()
        if person := cls.from_db(pid=pid, db=db):
            return person
        else:
            if not tm:
                tm = TmdbManager()
            person = cls.from_tmdb(pid=pid, tm=tm)
            if person:
                db.save_person(person)
            return person

    def __str__(self):
        s = self.name
        bd = self.birthday
        if dd := self.deathday:
            age = relativedelta(dd, bd).years
            s += f" ({bd.year}–{dd.year}|{age})"
        else:
            s += f" (b. {bd.year})"
        return s

    @property
    def details(self) -> dict:
        return self.data["details"]

    @property
    def name(self) -> str:
        return self.details["name"]

    @property
    def birthday(self) -> datetime.date:
        return datetime.datetime.strptime(
            self.details["birthday"], "%Y-%m-%d"
        ).date()

    @property
    def deathday(self) -> datetime.date | None:
        if dd := self.details.get("deathday"):
            return datetime.datetime.strptime(dd, "%Y-%m-%d").date()
        else:
            return None

    @property
    def url(self) -> str:
        return f"https://www.themoviedb.org/person/{self.pid}"

    @property
    def imdb_url(self) -> str | None:
        if iid := self.details.get("imdb_id"):
            return f"https://www.imdb.com/name/{iid}"
        else:
            return None

    @property
    def is_dead(self) -> bool:
        return bool(self.deathday)
