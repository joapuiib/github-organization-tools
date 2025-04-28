import pytest
import sys

from unittest.mock import MagicMock, patch
from ghot.ghot import main

@pytest.mark.parametrize("args, expected_kwargs", [
        pytest.param( # Default
            ["ghot", "config", "section.key", "value"],
            {"global_scope": False},
            id="default"
        ),
        pytest.param( # Default global
            ["ghot", "config", "--global", "section.key", "value"],
            {"global_scope": True},
            id="default_global"
        ),
        pytest.param( # Set
            ["ghot", "config", "set", "section.key", "value"],
            {"global_scope": False},
            id="set"
        ),
        pytest.param( # Set global
            ["ghot", "config", "set", "--global", "section.key", "value"],
            {"global_scope": True},
            id="set_global"
        ),
    ]
)
@patch("ghot.ghot.write_config", autospec=True)
def test_config_set(mock_write_config, args, expected_kwargs, monkeypatch):
    monkeypatch.setattr(sys, "argv", args)

    main()

    mock_write_config.assert_called_once_with(
        "section.key", "value", **expected_kwargs
    )
