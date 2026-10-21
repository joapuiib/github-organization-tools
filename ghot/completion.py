import os
import re
import sys
from pathlib import Path

import shtab

SHELLS = ["bash", "zsh", "tcsh"]

INSTALL_NOTES = {
    "zsh": "Make sure ~/.zfunc is in your fpath before compinit "
           "(fpath=(~/.zfunc $fpath)), then restart your shell.",
}

VERSION_STAMP = "# ghot-completion-version: "
SUPPRESS_WARNING_ENV = "GHOT_NO_COMPLETION_WARNING"


def install_paths():
    home = Path.home()
    return {
        "bash": home / ".local/share/bash-completion/completions/ghot",
        "zsh": home / ".zfunc/_ghot",
    }


def generate_completion(parser, shell, version):
    # The stamp goes last: zsh requires #compdef to be the first line
    return f"{shtab.complete(parser, shell=shell)}\n{VERSION_STAMP}{version}\n"


def install_completion(parser, shell, version):
    path = install_paths().get(shell)
    if path is None:
        raise ValueError(f"--install is not supported for {shell}. Use 'ghot completion {shell}' and install it manually.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_completion(parser, shell, version))
    print(f"Completion installed to {path}")
    if shell in INSTALL_NOTES:
        print(INSTALL_NOTES[shell])


def installed_version(path):
    """Version stamped in an installed completion script, or None if it has none."""
    try:
        match = re.search(rf"^{re.escape(VERSION_STAMP)}(\S+)\s*$", path.read_text(), re.MULTILINE)
    except OSError:
        return None
    return match.group(1) if match else None


def warn_if_outdated(version):
    """Warns on stderr about installed completion scripts that come from another version."""
    if os.environ.get(SUPPRESS_WARNING_ENV, "").strip().lower() in ("1", "true", "yes"):
        return
    for shell, path in install_paths().items():
        if not path.exists():
            continue
        if installed_version(path) != version:
            print(f"ghot: the {shell} completion script is outdated. "
                  f"Run 'ghot completion --install {shell}' and restart your shell.",
                  file=sys.stderr)
