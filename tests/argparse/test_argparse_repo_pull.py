import pytest
import sys

from unittest.mock import MagicMock, patch, create_autospec
from ghot.ghot import main
from ghot.org_manager import OrgManager


@pytest.mark.parametrize("args,expected_kwargs", [
    pytest.param(  # Default
        ["ghot", "repo", "pull", "users.csv"],
        {"dry": False, "destination": None},
        id="default"
    ),
    pytest.param(  # Dry
        ["ghot", "repo", "pull", "--dry", "users.csv"],
        {"dry": True, "destination": None},
        id="dry"
    ),
    pytest.param(  # Dest -d
        ["ghot", "repo", "pull", "-d", "repo-dest", "users.csv"],
        {"dry": False, "destination": "repo-dest"},
        id="dest-short"
    ),
    pytest.param(  # Dest --destination
        ["ghot", "repo", "pull", "--destination", "repo-dest", "users.csv"],
        {"dry": False, "destination": "repo-dest"},
        id="dest-long"
    ),
])
@patch("ghot.ghot.init_org_manager", autospec=True)
@patch("ghot.ghot.load_users", autospec=True)
def test_repo_pull(mock_load_users, mock_init_org_manager, args, expected_kwargs, monkeypatch):
    monkeypatch.setattr(sys, "argv", args)

    mock_org_manager = create_autospec(OrgManager)
    mock_init_org_manager.return_value = mock_org_manager

    mock_users = MagicMock(name="users")
    mock_load_users.return_value = mock_users

    main()

    mock_org_manager.repo_pull.assert_called_once_with(
        mock_users, **expected_kwargs
    )
