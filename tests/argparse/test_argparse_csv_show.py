import pytest
import sys
from unittest.mock import patch

from ghot.ghot import main


@pytest.mark.parametrize("args, config, expected_sources", [
    pytest.param(
        ["ghot", "csv", "show", "users.csv"],
        "",
        {"id": "default", "username": "default", "repo": "default", "description": "default"},
        id="default",
    ),
    pytest.param(
        ["ghot", "csv", "show", "users.csv"],
        "[csv]\npattern.id = {f1}\n",
        {"id": "config", "username": "default", "repo": "default", "description": "default"},
        id="config",
    ),
    pytest.param(
        ["ghot", "csv", "show", "--pattern-id", "{f1}", "--pattern-repo", "{f0}", "users.csv"],
        "[csv]\npattern.id = {f2}\n",
        {"id": "cli", "username": "default", "repo": "cli", "description": "default"},
        id="cli_overrides_config",
    ),
])
@patch("ghot.ghot.csv_show", autospec=True, return_value=0)
def test_csv_show_sources(mock_csv_show, args, config, expected_sources, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / ".ghot").write_text(config)
    monkeypatch.setattr(sys, "argv", args)

    main()

    loader, path, sources = mock_csv_show.call_args.args
    assert path == "users.csv"
    assert sources == expected_sources


@pytest.mark.parametrize("warnings, exit_code", [
    pytest.param(0, None, id="no_warnings"),
    pytest.param(3, 1, id="warnings"),
])
@patch("ghot.ghot.csv_show", autospec=True)
def test_csv_show_exit_code(mock_csv_show, warnings, exit_code, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setattr(sys, "argv", ["ghot", "csv", "show", "users.csv"])
    mock_csv_show.return_value = warnings

    if exit_code is None:
        main()
    else:
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == exit_code
