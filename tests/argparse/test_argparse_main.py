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
