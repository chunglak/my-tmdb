import os.path

OPE = os.path.expanduser
OPJ = os.path.join

ORGEE_ROAM_EXTDATA_ROOT = OPE("~/orgee-roam-extdata")
TMDB_MOVIES_ROOT = OPJ(ORGEE_ROAM_EXTDATA_ROOT, "tmdb", "movies")
TMDB_PERSONS_ROOT = OPJ(ORGEE_ROAM_EXTDATA_ROOT, "tmdb", "persons")

TMDB_KEY_FILE = OPE("~/.tmdb")
