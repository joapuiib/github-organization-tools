import pytest
from unittest.mock import MagicMock
from ghot.user import User

@pytest.mark.parametrize(
    "kwargs, user, title, body, expected_result",
    [
        pytest.param( # Invalid
            {},
            User(id=""),
            "title",
            "body",
            "invalid",
            id="invalid",
        ),
        pytest.param( # No repo
            {},
            User(id="test", username="member", repo=""),
            "title",
            "body",
            "no_repo",
            id="no_repo",
        ),
        pytest.param( # No title
            {},
            User(id="test", username="member", repo="exists"),
            "",
            "body",
            "no_title",
            id="no_title",
        ),
        pytest.param( # No body
            {},
            User(id="test", username="member", repo="exists"),
            "title",
            "",
            "no_body",
            id="no_body",
        ),
        pytest.param( # Repo not found
            {},
            User(id="test", username="member", repo="not_exists"),
            "title",
            "body",
            "repo_not_found",
            id="repo_not_found",
        ),
        pytest.param( # Issue created
            {},
            User(id="test", username="member", repo="exists"),
            "title",
            "body",
            ("issue_created", {"number": "issue_number"}),
            id="issue_created",
        ),
        pytest.param( # Issue created dry
            {"dry": True},
            User(id="test", username="member", repo="exists"),
            "title",
            "body",
            "issue_created_dry",
            id="issue_created_dry",
        ),
    ]
)
def test_process_issue_create(manager, kwargs, user, title, body, expected_result):
    org = manager._get_org("org")

    result = manager._process_issue_create(org, user, title, body, **kwargs)
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
def test_issue_create(manager, kwargs):
    title = "title"
    body = "body"
    users = [
        User(id=""), #Invalid
        User(id="test", username="member", repo=""), # No repo
        User(id="test", username="member", repo="not_exists"), # Repo not found
        User(id="test", username="member", repo="exists"), # Issue created
    ]
    manager.issue_create("org", users, title, body, **kwargs)
