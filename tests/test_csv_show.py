from io import StringIO
from unittest.mock import patch

import pytest

from ghot.csv_loader import CSVUserLoader
from ghot.csv_show import check_user, csv_show
from ghot.user import User

SOURCES = {"id": "default", "username": "default", "repo": "default", "description": "default"}


@pytest.mark.parametrize("user, expected", [
    pytest.param(User("id", "user", "repo"), [], id="valid"),
    pytest.param(User("", "user", "repo"), ["Empty id, row will be skipped"], id="empty_id"),
    pytest.param(User("id", "", "repo"), ["Empty username"], id="empty_username"),
    pytest.param(User("id", "user_1", "repo"), ["Invalid GitHub username 'user_1'"], id="invalid_username"),
    pytest.param(User("id", "-user", "repo"), ["Invalid GitHub username '-user'"], id="username_leading_hyphen"),
    pytest.param(User("id", "user", ""), ["Empty repo"], id="empty_repo"),
    pytest.param(User("id", "user", "my repo"), ["Invalid repository name 'my repo'"], id="invalid_repo"),
    pytest.param(User("id", "user", ".."), ["Invalid repository name '..'"], id="dot_repo"),
])
def test_check_user(user, expected):
    assert check_user(user) == expected


def run_csv_show(csv_content, capsys, ids=None, **patterns):
    loader = CSVUserLoader(
        pattern_id=patterns.get("id", "{f0}"),
        pattern_username=patterns.get("username", "{f1}"),
        pattern_repo=patterns.get("repo", "{f2}"),
        pattern_description=patterns.get("description", ""),
    )
    with patch('builtins.open', return_value=StringIO(csv_content), create=True):
        warnings = csv_show(loader, "users.csv", SOURCES, ids=ids)
    return warnings, capsys.readouterr().out


def test_csv_show_valid(capsys):
    warnings, out = run_csv_show("id,username,repo\nid1,user1,repo1\nid2,user2,repo2\n", capsys)

    assert warnings == 0
    assert "username 'user1', repo 'repo1'" in out
    assert "Total rows: 2" in out


def test_csv_show_duplicates(capsys):
    warnings, out = run_csv_show("id,username,repo\nid1,user1,repo1\nid1,user2,REPO1\n", capsys)

    assert warnings == 2
    assert "Duplicate id (also on line 2)" in out
    assert "Duplicate repo (also on line 2)" in out


def test_csv_show_skipped_row_uses_line(capsys):
    warnings, out = run_csv_show("id,username,repo\n,user1,repo1\n", capsys)

    assert warnings == 1
    assert "line 2" in out
    assert "Empty id, row will be skipped" in out


def test_csv_show_unknown_field(capsys):
    warnings, out = run_csv_show("id,username,repo\nid1,user1,repo1\n", capsys, repo="{missing}")

    assert warnings == 1
    assert "Could not read row: Field 'missing' not found in schema" in out


def test_csv_show_ids(capsys):
    warnings, out = run_csv_show("id,username,repo\nid1,user1,repo1\nid2,user2,repo2\n", capsys, ids=["id2"])

    assert warnings == 0
    assert "repo 'repo2'" in out
    assert "repo 'repo1'" not in out
    assert "Total rows: 1" in out


def test_csv_show_ids_duplicate_outside_filter(capsys):
    warnings, out = run_csv_show("id,username,repo\nid1,user1,repo1\nid2,user2,REPO1\n", capsys, ids=["id2"])

    assert warnings == 1
    assert "Duplicate repo (also on line 2)" in out


def test_csv_show_ids_not_found(capsys):
    warnings, out = run_csv_show("id,username,repo\nid1,user1,repo1\n", capsys, ids=["nope"])

    assert warnings == 1
    assert "nope" in out
    assert "Id not found" in out
