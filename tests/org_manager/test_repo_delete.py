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
            User(id="test", username="", repo=""),
            "no_repo",
            id="no_repo",
        ),
        pytest.param( # Repo not found
            {},
            User(id="test", username="", repo="not_exists"),
            "repo_not_found",
            id="repo_not_found",
        ),
        pytest.param( # Deletion skipped
            {},
            User(id="test", username="", repo="exists_cancelled"),
            "deletion_skipped",
            id="deletion_skipped",
        ),
        pytest.param( # Deletion dry
            {"dry": True},
            User(id="test", username="", repo="exists"),
            "deleted_dry",
            id="deleted_dry",
        ),
        pytest.param( # Deletion
            {},
            User(id="test", username="", repo="exists"),
            "deleted",
            id="deleted",
        ),
    ]
)
def test_process_repo_delete(manager, kwargs, user, expected_result):
    org = manager._get_org("org")

    result = manager._process_repo_delete(org, user, **kwargs)
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
            pytest.param( # Force
                {"force": True},
                id="force",
            ),
            pytest.param( # Force dry
                {"force": True, "dry": True},
                id="force_dry",
            ),
        ]
)
def test_repo_delete(manager, kwargs):
    users = [
        User(id=""), #Invalid
        User(id="test", username="", repo=""), # No repo
        User(id="test", username="", repo="not_exists"), # Repo not found
        User(id="test", username="", repo="exists_cancelled"), # Deletion skipped
        User(id="test", username="", repo="exists"), # Deletion
    ]
    manager.repo_delete("org", users, **kwargs)
