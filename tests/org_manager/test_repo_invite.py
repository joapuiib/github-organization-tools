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
        pytest.param( # No username
            {},
            User(id="test", username=""),
            "no_username",
            id="no_username",
        ),
        pytest.param( # No repo
            {},
            User(id="test", username="username"),
            "no_repo",
            id="no_repo",
        ),
        pytest.param( # User not found
            {},
            User(id="test", username="not_exists", repo="repo"),
            "user_not_found",
            id="user_not_found",
        ),
        pytest.param( # No org member
            {},
            User(id="test", username="no_org_member", repo="repo"),
            "no_org_member",
            id="no_org_member",
        ),
        pytest.param( # Repo not found
            {},
            User(id="test", username="member", repo="not_exists"),
            "repo_not_found",
            id="repo_not_found",
        ),
        pytest.param( # Already collaborator
            {},
            User(id="test", username="repo_collaborator", repo="repo"),
            "already_collaborator",
            id="already_collaborator",
        ),
        pytest.param( # Already invited
            {},
            User(id="test", username="repo_invited", repo="repo"),
            "already_invited",
            id="already_invited",
        ),
        pytest.param( # Invited (dry)
            {"dry": True},
            User(id="test", username="member", repo="repo"),
            "invite_dry",
            id="invite_dry",
        ),
        pytest.param( # Invited
            {},
            User(id="test", username="member", repo="repo"),
            "invite",
            id="invite",
        ),
    ]
)
def test_process_repo_invite(manager, kwargs, user, expected_result):
    org = manager._get_org("org")
    org_members = [m.login.lower() for m in org.get_members()]

    result = manager._process_repo_invite(org, user, org_members, **kwargs)
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
def test_repo_invite(manager, kwargs):
    users = [
        User(id=""), #Invalid
        User(id="test", username=""), # No username
        User(id="test", username="username"), # No repo
        User(id="test", username="not_exists", repo="repo"), # User not found
        User(id="test", username="no_org_member", repo="repo"), # No org member
        User(id="test", username="member", repo="not_exists"), # Repo not found
        User(id="test", username="repo_collaborator", repo="repo"), # Already collaborator
        User(id="test", username="repo_invited", repo="repo"), # Already invited
        User(id="test", username="member", repo="repo"), # Invited
    ]
    manager.repo_invite("org", users, **kwargs)
