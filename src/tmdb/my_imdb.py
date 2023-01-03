from __future__ import annotations  # PEP 585

import logging

from imdb import Cinemagoer  # type:ignore


class ImdbManager:
    def __init__(self) -> None:
        self.ia = Cinemagoer()

    def get_movie(self, mid: str) -> dict | None:
        if not mid.startswith("tt"):
            logging.error('Movie IDs should start with "tt"')
            return None
        try:
            movie = self.ia.get_movie(mid[2:])
        except ImdbDataAccessError:
            logging.error("Movie with id %s not found", mid)
            return None
