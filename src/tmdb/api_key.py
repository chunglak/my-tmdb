from __future__ import annotations  # PEP 585

import os.path

from .const import TMDB_KEY_FILE


def get_api_key(key_file: str | None = None) -> str:
    """
    Fetch the API key from a local file instead of hard-coding it
    """
    if not key_file:
        key_file = TMDB_KEY_FILE
    with open(key_file, "r", encoding="utf-8") as fh:
        return fh.read().strip()
