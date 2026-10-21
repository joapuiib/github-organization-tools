---
icon: octicons/terminal-16
alias: completion
---

# Shell Completion
`ghot` can generate completion scripts so that your shell completes
commands, subcommands, options, organization names and CSV files when you press ++tab++.

Scripts are available for __bash__, __zsh__ and __tcsh__.

## Printing the Completion Script
The script is printed to the standard output with the command:

```bash
ghot completion <shell>
```

- `<shell>`: the shell to generate the script for (`bash`, `zsh` or `tcsh`).

This is useful to load the completions only in the current session,
or to install the script manually in the location your shell expects.

??? example "Example: Enabling completions in the current bash session"
    ```bash
    eval "$(ghot completion bash)"
    ```

    The completions stay active until the session is closed.


## Installing the Completion Script
To install the script permanently in your user directory, add the `--install` option:

```bash
ghot completion --install <shell>
```

The script is written to a different location depending on the shell:

| Shell  | Location                                           |
|--------|----------------------------------------------------|
| `bash` | `~/.local/share/bash-completion/completions/ghot`  |
| `zsh`  | `~/.zfunc/_ghot`                                   |

Restart your shell to start using the completions.

!!! important "The installed script is a snapshot, so reinstall it after upgrading `ghot`."
    When `ghot` detects that the installed script comes from another version,
    it prints a warning on `stderr` with the command to run.

    To silence it, set the environment variable `GHOT_NO_COMPLETION_WARNING` to `1`:

    ```bash
    export GHOT_NO_COMPLETION_WARNING=1
    ```

!!! note "For `zsh`, the `~/.zfunc` directory must be in your `fpath` before `compinit` is called."
    ```zsh
    fpath=(~/.zfunc $fpath)
    autoload -Uz compinit && compinit
    ```

!!! warning "`--install` is not supported for `tcsh`."
    Use `ghot completion tcsh` and add the output to your shell configuration manually.


## What Is Completed
Besides commands and options, two arguments get a specific completion:

- __`<csv>`__: only directories and `.csv` files are suggested.
- __`<org>`__: the organizations of the authenticated user, fetched from GitHub.

The list of organizations is __cached__ for one hour in `~/.cache/ghot/orgs.json`
(or `$XDG_CACHE_HOME/ghot/orgs.json`), so pressing ++tab++ does not call the GitHub API every time.
If the list cannot be refreshed, for instance when you are offline or not authenticated,
the last cached list is used and no error is shown. To force a refresh, delete the cache file.
