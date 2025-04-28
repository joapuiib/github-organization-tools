import pytest
from unittest.mock import patch, MagicMock, call
from git.exc import InvalidGitRepositoryError
from ghot.user import User

@pytest.mark.parametrize(
    "kwargs, user, expected_result, expected_calls",
    [
        pytest.param( # Invalid
            {},
            User(id=""),
            "invalid",
            [],
            id="invalid",
        ),
        pytest.param( # No repo
            {},
            User(id="test", username="member", repo=""),
            "no_repo",
            [],
            id="no_repo",
        ),
        pytest.param( # Repo not cloned on disk
            {},
            User(id="not_cloned", username="member", repo="exists"),
            "repo_not_cloned",
            [],
            id="repo_not_found",
        ),
        pytest.param( # Repo pulled dry
            {"dry": True},
            User(id="dir", username="member", repo="exists"),
            "repo_pull_dry",
            [],
            id="repo_pull_dry",
        ),
        pytest.param( # Repo pulled
            {},
            User(id="dir", username="member", repo="exists"),
            "repo_pull",
            [call("dir")],
            id="repo_pull_dest",
        ),
        pytest.param( # Repo pulled with dest
            {"destination": "dest"},
            User(id="dir", username="member", repo="exists"),
            "repo_pull",
            [call("dest/dir")],
            id="repo_pull_dest",
        ),
        pytest.param( # Error pulling
            {},
            User(id="dir_no_repo", username="member", repo="exists"),
            "error_pulling",
            [call("dir_no_repo")],
            id="repo_pull_dest",
        ),
    ]
)
@patch("git.Repo")
@patch("os.path.isdir", side_effect=lambda x: "dir" in x)
def test_process_repo_pull(isdir, repo_mock, manager, kwargs, user, expected_result, expected_calls):
    def repo_mock_side_effect(x):
        if "no_repo" in x:
            raise InvalidGitRepositoryError("No repo")
        mock = MagicMock()
        return mock
    repo_mock.side_effect = repo_mock_side_effect

    result = manager._process_repo_pull(user, **kwargs)
    assert result == expected_result

    if len(expected_calls) > 0:
        repo_mock.assert_has_calls(expected_calls, any_order=True)
    else:
        repo_mock.assert_not_called()


@pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param( # Default
                {},
                id="default",
            ),
            pytest.param( # Dest
                {"destination": "dest"},
                id="dest",
            ),
            pytest.param( # Dest dry
                {"destination": "dest", "dry": True},
                id="dest_dry",
            ),
        ]
)
@patch("git.Repo")
@patch("os.path.isdir", side_effect=lambda x: "dir" in x)
def test_repo_pull(isdir, repo_mock, manager, kwargs):
    def repo_mock_side_effect(x):
        if "no_repo" in x:
            raise InvalidGitRepositoryError("No repo")
        mock = MagicMock()
        return mock
    repo_mock.side_effect = repo_mock_side_effect

    users = [
        User(id=""), # Invalid
        User(id="test", username="member", repo=""), # No repo
        User(id="not_cloned", username="member", repo="exists"), # Repo not found on disk
        User(id="dir", username="member", repo="exists"), # Repo pulled
        User(id="dir_no_repo", username="member", repo="exists"), # Error pulling
    ]
    manager.repo_pull(users, **kwargs)
