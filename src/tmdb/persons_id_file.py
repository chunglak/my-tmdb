from __future__ import annotations  # PEP 585

import json

from .db import TmdbDb
from .person import TmdbPerson


def make_tmdb_persons_id_file(fn: str):
    def process(tu: tuple) -> str:
        pid, js = tu
        p = TmdbPerson(pid=pid, data=json.loads(js))
        return f"{p} :: {pid}"

    db = TmdbDb()
    aps = db.all_person_ids()
    with open(fn, "w", encoding="utf8") as fh:
        fh.write("\n".join(map(process, sorted(aps))))
        fh.write("\n")
