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
        pytest.param( # User not found
            {},
            User(id="test", username="not_exists"),
            "user_not_found",
            id="user_not_found",
        ),
        pytest.param( # Member
            {},
            User(id="test", username="member"),
            "member",
            id="member",
        ),
        pytest.param( # Already invited
            {},
            User(id="test", username="org_invited"),
            "already_invited",
            id="already_invited",
        ),
        pytest.param( # Invited (dry)
            {"dry": True},
            User(id="test", username="no_member"),
            "invite_dry",
            id="invite_dry",
        ),
        pytest.param( # Invited
            {},
            User(id="test", username="no_member"),
            "invite",
            id="invite",
        ),
    ]
)
def test_process_user_invite(manager, kwargs, user, expected_result):
    org = manager._get_org("org")
    org_members = [m.login.lower() for m in org.get_members()]
    org_invitations = [i.login.lower() for i in org.invitations()]

    result = manager._process_user_invite(org, user, org_members, org_invitations, **kwargs)
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
def test_user_invite(manager, kwargs):
    users = [
        User(id=""), #Invalid
        User(id="test", username=""), # No username
        User(id="test", username="not_exists"), # User not found
        User(id="test", username="member"), # Member
        User(id="test", username="org_invited"), # Already invited
        User(id="test", username="no_member"), # Invited
    ]
    manager.user_invite("org", users, **kwargs)

