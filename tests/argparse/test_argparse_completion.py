import pytest
import sys

from pathlib import Path

from unittest.mock import patch
from ghot.ghot import main, __version__


@pytest.mark.parametrize("shell", ["bash", "zsh", "tcsh"])
def test_completion_prints_script(monkeypatch, capsys, shell):
    monkeypatch.setattr(sys, "argv", ["ghot", "completion", shell])

    main()

    out = capsys.readouterr().out
    assert "ghot" in out
    assert "repo" in out


@patch('ghot.ghot.install_completion')
def test_completion_install(mock_install, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ghot", "completion", "--install", "bash"])

    main()

    mock_install.assert_called_once()
    assert mock_install.call_args[0][1] == "bash"
    assert mock_install.call_args[0][2] == __version__


def test_completion_install_unsupported_shell(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ghot", "completion", "--install", "tcsh"])

    with pytest.raises(SystemExit):
        main()


@pytest.fixture
def fake_home(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path


def test_installed_script_is_stamped(monkeypatch, fake_home):
    monkeypatch.setattr(sys, "argv", ["ghot", "completion", "--install", "bash"])

    main()

    path = fake_home / ".local/share/bash-completion/completions/ghot"
    assert path.read_text().rstrip().endswith(f"# ghot-completion-version: {__version__}")


def test_zsh_compdef_stays_first_line(monkeypatch, fake_home):
    monkeypatch.setattr(sys, "argv", ["ghot", "completion", "--install", "zsh"])

    main()

    assert (fake_home / ".zfunc/_ghot").read_text().startswith("#compdef")


@patch('ghot.ghot.handle_auth')
def test_warns_when_installed_script_is_outdated(mock_auth, monkeypatch, capsys, fake_home):
    path = fake_home / ".local/share/bash-completion/completions/ghot"
    path.parent.mkdir(parents=True)
    path.write_text("# ghot-completion-version: 0.0.1\n")
    monkeypatch.setattr(sys, "argv", ["ghot", "auth", "check"])

    main()

    assert "outdated" in capsys.readouterr().err


@patch('ghot.ghot.handle_auth')
def test_no_warning_when_up_to_date_or_not_installed(mock_auth, monkeypatch, capsys, fake_home):
    monkeypatch.setattr(sys, "argv", ["ghot", "auth", "check"])
    main()
    assert capsys.readouterr().err == ""

    path = fake_home / ".local/share/bash-completion/completions/ghot"
    path.parent.mkdir(parents=True)
    path.write_text(f"# ghot-completion-version: {__version__}\n")
    main()
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("value", ["1", "true", "yes"])
@patch('ghot.ghot.handle_auth')
def test_warning_can_be_suppressed(mock_auth, monkeypatch, capsys, fake_home, value):
    path = fake_home / ".local/share/bash-completion/completions/ghot"
    path.parent.mkdir(parents=True)
    path.write_text("# ghot-completion-version: 0.0.1\n")
    monkeypatch.setenv("GHOT_NO_COMPLETION_WARNING", value)
    monkeypatch.setattr(sys, "argv", ["ghot", "auth", "check"])

    main()

    assert capsys.readouterr().err == ""
