from __future__ import annotations  # PEP 585

import datetime
import json
import os.path
import traceback
from dataclasses import dataclass

from ..const import TMDB_MOVIES_ROOT
from .tmdb import TmdbManager


@dataclass
class TmdbMovie:
    mid: int

    @classmethod
    def from_imdb_id(cls, imdb_id: str, tm: TmdbManager) -> TmdbMovie | None:
        if r := tm.find_movie_id_by_imdb_id(imdb_id=imdb_id):
            return TmdbMovie(mid=r["id"])
        else:
            return None

    def path(self) -> str:
        return os.path.join(TMDB_MOVIES_ROOT, "%s.json" % self.mid)

    def local_exists_p(self) -> bool:
        return os.path.isfile(self.path())

    def load_data(self, tm: TmdbManager | None = None) -> dict | None:
        path = self.path()
        if not os.path.isfile(path):
            if tm:
                try:
                    data = self.fetch_data(tm=tm)
                except:  # pylint: disable=bare-except
                    traceback.print_exc()  # to stderr
                    return None
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
            "details": tm.get_movie_details(mid=self.mid),
            "credits": tm.get_movie_credits(mid=self.mid),
            "external_ids": tm.get_movie_external_ids(mid=self.mid),
            "keywords": tm.get_movie_keywords(mid=self.mid),
        }
