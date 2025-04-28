import pytest
import sys

from unittest.mock import MagicMock, patch, create_autospec
from ghot.ghot import main
from ghot.org_manager import OrgManager

@pytest.mark.parametrize("args,expected_kwargs", [
    pytest.param(  # Default
        ["ghot", "repo", "delete", "org", "users.csv"],
        {"dry": False, "force": False},
        id="default"
    ),
    pytest.param(  # Dry
        ["ghot", "repo", "delete", "--dry", "org", "users.csv"],
        {"dry": True, "force": False},
        id="dry"
    ),
    pytest.param(  # Force
        ["ghot", "repo", "delete", "--force", "org", "users.csv"],
        {"dry": False, "force": True},
        id="force"
    ),
])
@patch("ghot.ghot.init_org_manager", autospec=True)
@patch("ghot.ghot.load_users", autospec=True)
def test_repo_delete(mock_load_users, mock_init_org_manager, args, expected_kwargs, monkeypatch):
    monkeypatch.setattr(sys, "argv", args)

    mock_org_manager = create_autospec(OrgManager)
    mock_init_org_manager.return_value = mock_org_manager

    mock_users = MagicMock(name="users")
    mock_load_users.return_value = mock_users

    main()

    mock_org_manager.repo_delete.assert_called_once_with(
        "org", mock_users, **expected_kwargs
    )
