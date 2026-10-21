import json
import time
from unittest.mock import MagicMock, patch

import pytest

from ghot import org_cache


@pytest.fixture(autouse=True)
def cache_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    return tmp_path


def write(cache_dir, orgs, age=0):
    path = cache_dir / "ghot" / "orgs.json"
    path.parent.mkdir()
    path.write_text(json.dumps({"timestamp": time.time() - age, "orgs": orgs}))


@patch('ghot.org_cache.fetch_orgs')
def test_fresh_cache_is_used(mock_fetch, cache_dir):
    write(cache_dir, ["cached"])
    assert org_cache.list_orgs() == ["cached"]
    mock_fetch.assert_not_called()


@patch('ghot.org_cache.fetch_orgs', return_value=["new"])
def test_stale_cache_is_refreshed(mock_fetch, cache_dir):
    write(cache_dir, ["old"], age=org_cache.CACHE_TTL + 1)
    assert org_cache.list_orgs() == ["new"]
    assert org_cache.read_cache() == (["new"], True)


@patch('ghot.org_cache.fetch_orgs', side_effect=RuntimeError("offline"))
def test_stale_cache_used_on_error(mock_fetch, cache_dir):
    write(cache_dir, ["old"], age=org_cache.CACHE_TTL + 1)
    assert org_cache.list_orgs() == ["old"]


@patch('ghot.org_cache.fetch_orgs', return_value=None)
def test_no_token_no_cache(mock_fetch):
    assert org_cache.list_orgs() == []


@patch('ghot.org_cache.AuthManager')
def test_fetch_orgs_sorted(mock_auth):
    auth = mock_auth.return_value
    auth.has_token.return_value = True
    auth.client().get_user().get_orgs.return_value = [MagicMock(login="b"), MagicMock(login="a")]
    assert org_cache.fetch_orgs() == ["a", "b"]
