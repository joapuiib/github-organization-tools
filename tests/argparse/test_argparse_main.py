import pytest
import sys

from ghot.ghot import __version__, main

@pytest.mark.parametrize("flag", ["--version", "-V"])
def test_version(flag, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ghot", flag])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    assert capsys.readouterr().out == f"ghot {__version__}\n"


def test_no_args_prints_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ghot"])

    main()

    assert capsys.readouterr().out.startswith("usage: ghot")


@pytest.mark.parametrize("args, expected_usage", [
    pytest.param(["ghot", "-h"], "usage: ghot [-h] [-V] <command>", id="main"),
    pytest.param(["ghot", "repo", "-h"], "usage: ghot repo [-h] <command>", id="repo"),
    pytest.param(["ghot", "config", "-h"], "usage: ghot config [-h] <command>", id="config"),
])
def test_help(args, expected_usage, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", args)

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith(expected_usage)


@pytest.mark.parametrize("command", ["auth", "config", "csv", "user", "repo", "issue"])
def test_command_without_subcommand_prints_help(command, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ghot", command])

    main()

    assert capsys.readouterr().out.startswith(f"usage: ghot {command} [-h] <command>")
