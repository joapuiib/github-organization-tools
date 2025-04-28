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
        pytest.param( # Repo already cloned
            {},
            User(id="dir_test", username="member", repo="exists"),
            "repo_already_cloned",
            [call("dir_test")],
            id="repo_already_cloned",
        ),
        pytest.param( # Dir exists but not a repo
            {},
            User(id="dir_no_repo", username="member", repo="exists"),
            "exists_but_not_repo",
            [call("dir_no_repo")],
            id="exists_but_no_repo",
        ),
        pytest.param( # Repo not found
            {},
            User(id="test", username="member", repo="not_exists"),
            "repo_not_found",
            [],
            id="repo_not_found",
        ),
        pytest.param( # Repo cloned dry
            {"dry": True},
            User(id="test", username="member", repo="exists"),
            "repo_cloned_dry",
            [],
            id="repo_cloned_dry",
        ),
        pytest.param( # Repo cloned
            {},
            User(id="test", username="member", repo="exists"),
            "repo_cloned",
            [call.clone_from("HTTPS_URL/org/exists", "test")],
            id="repo_cloned",
        ),
        pytest.param( # Repo cloned with dest
            {"destination": "dest"},
            User(id="test", username="member", repo="exists"),
            "repo_cloned",
            [call.clone_from("HTTPS_URL/org/exists", "dest/test")],
            id="repo_cloned_dest",
        ),
        pytest.param( # Repo cloned with SSH
            {"ssh": True},
            User(id="test", username="member", repo="exists"),
            "repo_cloned",
            [call.clone_from("SSH_URL/org/exists", "test")],
            id="repo_cloned_ssh",
        ),
    ]
)
@patch("git.Repo")
@patch("os.path.isdir", side_effect=lambda x: "dir" in x)
def test_process_repo_clone(isdir, repo_mock, manager, kwargs, user, expected_result, expected_calls):
    def repo_mock_side_effect(x):
        if "no_repo" in x:
            raise InvalidGitRepositoryError("No repo")
        mock = MagicMock()
        return mock
    repo_mock.side_effect = repo_mock_side_effect

    org = manager._get_org("org")

    result = manager._process_repo_clone(org, user, **kwargs)
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
            pytest.param( # SSH
                {"ssh": True},
                id="ssh",
            ),
            pytest.param( # Dry
                {"dry": True},
                id="dry",
            ),
            pytest.param( # Dest dry
                {"destination": "dest", "dry": True},
                id="dest_dry",
            ),
        ]
)
@patch("git.Repo")
@patch("os.path.isdir", side_effect=lambda x: "dir" in x)
def test_repo_clone(isdir, repo_mock, manager, kwargs):
    def repo_mock_side_effect(x):
        if "no_repo" in x:
            raise InvalidGitRepositoryError("No repo")
        mock = MagicMock()
        return mock
    repo_mock.side_effect = repo_mock_side_effect

    users = [
        User(id=""), # Invalid
        User(id="test", username="member", repo=""), # No repo
        User(id="dir_test", username="member", repo="exists"), # Repo already cloned
        User(id="dir_no_repo", username="member", repo="exists"), # Dir exists but not a repo
        User(id="test", username="member", repo="not_exists"), # Repo not found
        User(id="test", username="member", repo="exists"), # Repo cloned
    ]
    manager.repo_clone("org", users, **kwargs)
