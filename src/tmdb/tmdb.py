from __future__ import annotations  # PEP 585

import urllib.parse

import requests

from .api_key import get_api_key

TIMEOUT = 5


class TmdbManager:
    def __init__(self, key_file: str | None = None) -> None:
        self.api_key = get_api_key(key_file=key_file)
        self.pattern = (
            "https://api.themoviedb.org/3/%%s?api_key=%s" % self.api_key
        )

    def get(self, route: str, parms: dict | None = None) -> dict:
        url = self.pattern % route
        if parms:
            url += "&" + urllib.parse.urlencode(parms)
        r = requests.get(url, timeout=5)
        if r.ok:
            return r.json()
        else:
            raise Exception(f"Error: {r.reason} ({r.status_code})")

    def find_id_by_imdb_id(self, imdb_id: str) -> dict:
        return self.get(f"find/{imdb_id}", parms={"external_source": "imdb_id"})

    def find_movie_id_by_imdb_id(self, imdb_id) -> dict | None:
        r = self.find_id_by_imdb_id(imdb_id=f"tt{imdb_id}")
        if mr := r.get("movie_results"):
            return mr[0]
        else:
            return None

    def find_person_id_by_imdb_id(self, imdb_id) -> dict | None:
        r = self.find_id_by_imdb_id(imdb_id=f"nm{imdb_id}")
        if mr := r.get("person_results"):
            return mr[0]
        else:
            return None

    def get_movie_details(self, mid: int) -> dict:
        return self.get(f"movie/{mid}")

    def get_movie_credits(self, mid: int) -> dict:
        return self.get(f"movie/{mid}/credits")

    def get_movie_external_ids(self, mid: int) -> dict:
        return self.get(f"movie/{mid}/external_ids")

    def get_movie_keywords(self, mid: int) -> dict:
        return self.get(f"movie/{mid}/keywords")

    def get_person_details(self, pid: int) -> dict:
        return self.get(f"person/{pid}")

    def get_person_movie_credits(self, pid: int) -> dict:
        return self.get(f"person/{pid}/movie_credits")

    def get_person_tv_credits(self, pid: int) -> dict:
        return self.get(f"person/{pid}/tv_credits")

    def get_person_external_ids(self, pid: int) -> dict:
        return self.get(f"person/{pid}/external_ids")
