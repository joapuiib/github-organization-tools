---
icon: material/tools
alias: config
---

# Configuration

GitHub Organization Tools uses a configuration file system similar to [`git-config`][git-cinfig] to manage tool settings.

[git-config]: https://git-scm.com/docs/git-config

## Configuration Files

The tool reads configuration values from two sources, where local values override global ones:

- `~/.ghot`: Global configuration file (applies to all invocations).
- `.ghot`: Local configuration file (applies to invocations in the current directory).


## Setting a Configuration Value

To set a configuration key, use the following command:

```bash
ghot config [set] [--global] <key> <value>
```

- `set` (optional): This is the default behaviour and can be omitted. Explicitly indicates you're setting a value.

- `--global` (optional): Applies the setting to the global configuration file (`~/.ghot`). If omitted, the setting is written to the local configuration file (`.ghot`) in the current directory.

- `<key>`: The configuration key to set.

- `<value>`: The value to assign to the key


## Viewing a Configuration Value

To retrieve the current value of a configuration key, use the `show` command:

```bash
ghot config show [<key>]
```

- `<key>` (optional): The configuration key to display. If omitted, all configuration keys are shown.
    If the key is defined in both global and local files, the local value is shown.

## List of Configuration Keys

### [[csv#pattern-options|CSV Options]]
| Config Key | CLI Option | Default Value | Description |
|--------|---------------|-------------|--------|
| `csv.pattern.id` | `--pattern-id` | `{id}` | Pattern for [`id` field][fields]. |
| `csv.pattern.username` | `--pattern-username` | `{username}` | Pattern for [`username` field][fields]. |
| `csv.pattern.repo` | `--pattern-repo` | `{repo}` | Pattern for [`repo` field][fields]. |
| `csv.pattern.description` | `--pattern-description` | `""` | Pattern for [`description` field][fields]. |

[fields]: ../options/csv.md#fields
