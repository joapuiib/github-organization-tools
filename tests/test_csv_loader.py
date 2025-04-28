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


