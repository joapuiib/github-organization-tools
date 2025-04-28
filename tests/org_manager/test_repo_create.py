import pytest
from ghot.user import User

@pytest.mark.parametrize(
    "kwargs, user, expected_result",
    [
        pytest.param( # Invalid
            {},
            User(id=""),
            "invalid",
            id="invalid",
        ),
        pytest.param( # No repo
            {},
            User(id="test", username="member", repo=""),
            "no_repo",
            id="no_repo",
        ),
        pytest.param( # Repo already exists
            {},
            User(id="test", username="member", repo="exists"),
            "repo_exists",
            id="repo_exists",
        ),
        pytest.param( # Repo created dry
            {"dry": True},
            User(id="test", username="member", repo="not_exists"),
            "repo_created_dry",
            id="repo_created_dry",
        ),
        pytest.param( # Repo created
            {},
            User(id="test", username="member", repo="not_exists"),
            "repo_created",
            id="repo_created",
        ),
    ]
)
def test_process_repo_create(manager, kwargs, user, expected_result):
    org = manager._get_org("org")

    result = manager._process_repo_create(org, user, **kwargs)
    assert result == expected_result


@pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param( # Default
                {},
                id="default",
            ),
            pytest.param( # Dry
                {"dry": True},
                id="dry",
            ),
        ]
)
def test_repo_create(manager, kwargs):
    users = [
        User(id=""), #Invalid
        User(id="test", username="member", repo=""), # No repo
        User(id="test", username="member", repo="exists"), # Repo already exists
        User(id="test", username="member", repo="not_exists"), # Repo created
    ]
    manager.repo_create("org", users, **kwargs)
