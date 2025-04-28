import pytest
from ghot.user import User

@pytest.mark.parametrize(
    "kwargs, user, expected_result",
    [
        pytest.param( # Invalid
            {},
            User(id=""),
            "invalid",
            id="default",
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
        pytest.param( # Not member
            {},
            User(id="test", username="not_member"),
            "not_member",
            id="not_member",
        ),
        pytest.param( # Invitation cancelled
            {},
            User(id="test", username="org_invited_cancelled"),
            "deletion_skipped",
            id="invitation_cancelled",
        ),
        pytest.param( # Invitation removed
            {},
            User(id="test", username="org_invited"),
            "invite_removed",
            id="invite_removed",
        ),
        pytest.param( # Invitation removed (dry)
            {"dry": True},
            User(id="test", username="org_invited"),
            "invite_removed_dry",
            id="invite_removed",
        ),
        pytest.param( # Removed cancelled
            {},
            User(id="test", username="member_cancelled"),
            "deletion_skipped",
            id="removed_cancelled",
        ),
        pytest.param( # Removed (dry)
            {"dry": True},
            User(id="test", username="member"),
            "removed_dry",
            id="removed_dry",
        ),
        pytest.param( # Removed
            {},
            User(id="test", username="member"),
            "removed",
            id="removed",
        ),
    ]
)
def test_process_user_remove(manager, kwargs, user, expected_result):
    org = manager._get_org("org")
    org_members = [m.login.lower() for m in org.get_members()]
    org_invitations = {i.login.lower() : i for i in org.invitations()}

    result = manager._process_user_remove(org, user, org_members, org_invitations, **kwargs)
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
        ]
)
def test_user_remove(manager, kwargs):
    users = [
        User(id=""), #Invalid
        User(id="test", username=""), # No username
        User(id="test", username="not_exists"), # User not found
        User(id="test", username="not_member"), # Not member
        User(id="test", username="org_invited_cancelled"), # Invitation cancelled
        User(id="test", username="org_invited"), # Invitation removed
        User(id="test", username="member_cancelled"), # Removed cancelled
        User(id="test", username="member"), # Removed
    ]
    manager.user_remove("org", users, **kwargs)

