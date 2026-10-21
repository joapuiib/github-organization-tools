import contextlib
import io
import json
import os
import time
from pathlib import Path

from .auth import AuthManager

CACHE_TTL = 3600  # seconds


def cache_path():
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "ghot" / "orgs.json"


def read_cache():
    """Returns (orgs, fresh). orgs is empty if there is no usable cache."""
    try:
        data = json.loads(cache_path().read_text(encoding="utf-8"))
        orgs = [str(org) for org in data["orgs"]]
        fresh = time.time() - data["timestamp"] < CACHE_TTL
        return orgs, fresh
    except (OSError, ValueError, KeyError, TypeError):
        return [], False


def write_cache(orgs):
    path = cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"timestamp": time.time(), "orgs": orgs}), encoding="utf-8")
    except OSError:
        pass


def fetch_orgs():
    auth = AuthManager()
    if not auth.has_token():
        return None
    return sorted(org.login for org in auth.client().get_user().get_orgs())


def list_orgs():
    """
    Organizations of the authenticated user, for shell completion.

    Uses a cached list while it is fresh, and falls back to a stale one if GitHub
    can't be reached. Never prompts and never raises: completion must stay silent.
    """
    orgs, fresh = read_cache()
    if fresh:
        return orgs

    try:
        with contextlib.redirect_stderr(io.StringIO()):
            fetched = fetch_orgs()
    except Exception:
        fetched = None

    if fetched is None:
        return orgs
    write_cache(fetched)
    return fetched
