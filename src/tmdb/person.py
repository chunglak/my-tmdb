from __future__ import annotations  # PEP 585

import datetime
import json
import os.path
from dataclasses import dataclass

from ..const import TMDB_PERSONS_ROOT
from .tmdb import TmdbManager


@dataclass
class TmdbPerson:
    pid: int

    @classmethod
    def from_imdb_id(cls, imdb_id: str, tm: TmdbManager) -> TmdbPerson | None:
        if r := tm.find_person_id_by_imdb_id(imdb_id=imdb_id):
            return TmdbPerson(pid=r["id"])
        else:
            return None

    def path(self) -> str:
        return os.path.join(TMDB_PERSONS_ROOT, "%s.json" % self.pid)

    def load_data(self, tm: TmdbManager | None = None) -> dict | None:
        path = self.path()
        if not os.path.isfile(path):
            if tm:
                data = self.fetch_data(tm=tm)
                with open(path, "w", encoding="utf8") as fh:
                    json.dump(data, fh, indent=2, ensure_ascii=False)
                return data
            else:
                return None
        else:
            with open(path, "r", encoding="utf8") as fh:
                return json.load(fh)

    def fetch_data(self, tm: TmdbManager) -> dict:
        return {
            "retrieved_dt": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "details": tm.get_person_details(pid=self.pid),
            "movie_credits": tm.get_person_movie_credits(pid=self.pid),
            "tv_credits": tm.get_person_tv_credits(pid=self.pid),
            "external_ids": tm.get_person_external_ids(pid=self.pid),
        }
