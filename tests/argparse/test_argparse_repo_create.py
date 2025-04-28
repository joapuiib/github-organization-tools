import pytest
import sys
from unittest.mock import MagicMock, patch, create_autospec
from ghot.ghot import main
from ghot.org_manager import OrgManager

@pytest.mark.parametrize("args,expected_kwargs", [
    pytest.param(  # Default
        ["ghot", "repo", "create", "org", "users.csv"],
        {"dry": False, "private": True},
        id="default"
    ),
    pytest.param(  # Explicit --private
        ["ghot", "repo", "create", "--private", "org", "users.csv"],
        {"dry": False, "private": True},
        id="explicit_private"
    ),
    pytest.param(  # Explicit --public
        ["ghot", "repo", "create", "--public", "org", "users.csv"],
        {"dry": False, "private": False},
        id="explicit_public"
    ),
    pytest.param(  # Private overrides public
        ["ghot", "repo", "create", "--private", "--public", "org", "users.csv"],
        {"dry": False, "private": True},
        id="private_overrides_public"
    ),
    pytest.param(  # Dry
        ["ghot", "repo", "create", "--dry", "org", "users.csv"],
        {"dry": True, "private": True},
        id="dry"
    ),
])
@patch("ghot.ghot.init_org_manager", autospec=True)
@patch("ghot.ghot.load_users", autospec=True)
def test_repo_create(mock_load_users, mock_init_org_manager, args, expected_kwargs, monkeypatch):
    monkeypatch.setattr(sys, "argv", args)

    mock_org_manager = create_autospec(OrgManager)
    mock_init_org_manager.return_value = mock_org_manager

    mock_users = MagicMock(name="users")
    mock_load_users.return_value = mock_users

    main()

    mock_org_manager.repo_create.assert_called_once_with(
        "org", mock_users, **expected_kwargs
    )
