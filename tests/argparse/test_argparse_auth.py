import pytest
import sys

from unittest.mock import MagicMock, patch, create_autospec
from ghot.ghot import main
from ghot.auth import AuthManager

@pytest.mark.parametrize("argv, mock_method", [
    pytest.param(  # Print token
        ["ghot", "auth", "print"],
        "print_token",
        id="print"
    ),
    pytest.param(  # Remove token
        ["ghot", "auth", "remove"],
        "remove_token",
        id="remove"
    ),
])
@patch('ghot.ghot.AuthManager')
def test_auth(mock_auth_manager, monkeypatch, argv, mock_method):
    mock_auth = create_autospec(AuthManager)
    mock_auth.client().get_user().login = "test-user"
    mock_auth_manager.return_value = mock_auth

    monkeypatch.setattr(sys, "argv", argv)

    main()

    getattr(mock_auth, mock_method).assert_called_once()
