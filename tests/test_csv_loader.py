from io import StringIO
from unittest.mock import patch

from ghot.csv_loader import CSVUserLoader
from ghot.user import User


def test_load():
    csv_content = """id,username,repository
123,johndoe,repo1
456,janedoe,repo2
"""
    f = StringIO(csv_content)

    loader = CSVUserLoader(
        pattern_id="{f0}",                  # index
        pattern_username="{username}",      # named
        pattern_repo="gh/{username}/{f2}",  # mixed pattern
        pattern_description="Repository for {username.upper()}", # filters
    )

    with patch('builtins.open', return_value=f, create=True):
        users = loader.load("fake_path.csv")

    expected = [
        User(id="123", username="johndoe", repo="gh/johndoe/repo1", description="Repository for JOHNDOE"),
        User(id="456", username="janedoe", repo="gh/janedoe/repo2", description="Repository for JANEDOE"),
    ]

    assert users == expected




def test_load_utf8_with_bom(tmp_path):
    path = tmp_path / "users.csv"
    path.write_bytes("﻿Nombre,username\nIVÁN,ivan\n".encode("utf-8"))

    loader = CSVUserLoader(
        pattern_id="{Nombre.lower()}",
        pattern_username="{username}",
    )

    assert loader.load(path) == [User(id="iván", username="ivan")]


def test_load_short_rows(tmp_path):
    path = tmp_path / "users.csv"
    path.write_text("id,repo,username\nid1,repo1\nid2,repo2,user2\n")

    loader = CSVUserLoader(
        pattern_id="{id}",
        pattern_username="{username}",
        pattern_repo="{repo}",
    )

    assert loader.load(path) == [
        User(id="id1", username="", repo="repo1"),
        User(id="id2", username="user2", repo="repo2"),
    ]
