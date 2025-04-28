import pytest
import sys

from unittest.mock import MagicMock, patch, create_autospec
from ghot.ghot import main
from ghot.org_manager import OrgManager

@pytest.mark.parametrize("args,expected_kwargs", [
    pytest.param(  # Default
        ["ghot", "repo", "clone", "org", "users.csv"],
        {"dry": False, "destination": None, "ssh": False},
        id="default"
    ),
    pytest.param(  # Dry
        ["ghot", "repo", "clone", "--dry", "org", "users.csv"],
        {"dry": True, "destination": None, "ssh": False},
        id="dry"
    ),
    pytest.param(  # Dest -d
        ["ghot", "repo", "clone", "-d", "repo-dest", "org", "users.csv"],
        {"dry": False, "destination": "repo-dest", "ssh": False},
        id="dest_short"
    ),
    pytest.param(  # Dest --destination
        ["ghot", "repo", "clone", "--destination", "repo-dest", "org", "users.csv"],
        {"dry": False, "destination": "repo-dest", "ssh": False},
        id="dest_long"
    ),
    pytest.param(  # SSH
        ["ghot", "repo", "clone", "--ssh", "org", "users.csv"],
        {"dry": False, "destination": None, "ssh": True},
        id="ssh"
    ),
])
@patch("ghot.ghot.init_org_manager", autospec=True)
@patch("ghot.ghot.load_users", autospec=True)
def test_repo_clone(mock_load_users, mock_init_org_manager, args, expected_kwargs, monkeypatch):
    monkeypatch.setattr(sys, "argv", args)

    mock_org_manager = create_autospec(OrgManager)
    mock_init_org_manager.return_value = mock_org_manager

    mock_users = MagicMock(name="users")
    mock_load_users.return_value = mock_users

    main()

    mock_org_manager.repo_clone.assert_called_once_with(
        "org", mock_users, **expected_kwargs
    )
