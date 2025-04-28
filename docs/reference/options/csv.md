---
icon: fontawesome/solid/file-csv
alias: csv
---

# CSV Format
GitHub Organization Tools uses a CSV file as the primary input for user and repository data.
This file contains rows representing users, and the tool maps specific columns
to fields such as user ID, GitHub username, and repository URL.

## Fields
`ghot` uses different fields depending on the command you are using.

| Field | Description | Default pattern |
|-------|-------------|---------|
| `id` | Identifier for the user in `ghot`. | `{0}` |
| `username` | The GitHub username of the user. | `{1}` |
| `repo` | The repository name whithin the organization. | `{2}` |
| `description` | Description of the repository. | `""` |

By default, `ghot` uses the colums first columns
to extract the data from the CSV file.

```csv
id,username,repo
user1,user1,user1-repo
user2,user2,user2-repo
```

This can be configured using [Patterns](#patterns) through CLI options or
through your [[config]].



## Patterns
You can control how `ghot` extracts data from the CSV using
CLI options or through your [[config]].

Patterns support:

- __Positional placeholders__ like `{f0}`, `{f1}`, etc. (referring to column index)
- __Named placeholders__ like `{username}`, `{repo}` (referring to CSV headers)
- __Default values__ like `{expr?default}` (if the expression is empty, use `default`)
- __Filters__ like `lower()` or `words()` to transform the data.

??? example "Example: Default Patterns"
    ```csv title="CSV file"
    id,username,repo
    user1,user1,user1-repo
    user2,user2,user2-repo
    ```

    | Field | Pattern | Result |
    |-------|---------|--------|
    | `id` | `{f0}` | `user1` |
    | `username` | `{f1}` | `user1` |
    | `repo` | `{f2}` | `user1-repo` |
    | `description` | `""` | `""` |

    === "CLI options"
        ```bash
        ghot user invite \
            --pattern-id "{f0}" \
            --pattern-username "{f1}" \
            --pattern-repo "{f2}" \
            --pattern-description "" \
            my-org users.csv
        ```
    === "Config"
        ```bash
        ghot config csv.pattern.id "{f0}"
        ghot config csv.pattern.username "{f1}"
        ghot config csv.pattern.repo "{f2}"
        ghot config csv.pattern.description ""
        ghot user invite my-org users.csv
        ```


??? example "Example: Default behaviour with named patterns"
    ```csv title="CSV file"
    id,username,repo
    user1,user1,user1-repo
    user2,user2,user2-repo
    ```

    | Field | Pattern | Result |
    |-------|---------|--------|
    | `id` | `{id}` | `user1` |
    | `username` | `{username}` | `user1` |
    | `repo` | `{repo}` | `user1-repo` |
    | `description` | `{description?}` | `""` |

    === "CLI options"
        ```bash
        ghot user invite \
            --pattern-id "{id}" \
            --pattern-username "{username}" \
            --pattern-repo "{repo}" \
            --pattern-description "{description?}" \
            my-org users.csv
        ```
    === "Config"
        ```bash
        ghot config csv.pattern.id "{id}"
        ghot config csv.pattern.username "{username}"
        ghot config csv.pattern.repo "{repo}"
        ghot config csv.pattern.description "{description?}"
        ghot user invite my-org users.csv
        ```

??? example "Example: Create repositories from usernames"
    ```csv title="CSV file"
    id,username,repo
    user1,user1,user1-repo
    user2,user2,user2-repo
    ```

    | Field | Pattern | Result |
    |-------|---------|--------|
    | `repo` | `{username}-repo` | `user1-repo` |
    | `description` | `Repository for {username}` | `Repository for user1` |

    === "CLI options"
        ```bash
        ghot repo create \
            --pattern-repo "{username}-repo" \
            --pattern-description "Repository for {username}" \
            my-org users.csv
        ```

    === "Config"
        ```bash
        ghot config csv.pattern.repo "{username}-repo"
        ghot config csv.pattern.description "Repository for {username}"
        ghot repo create my-org users.csv
        ```

## Filters
Filters are used to transform the data extracted from the CSV file.

| Filter | Description |
|--------|-------------|
| `lower()` | Converts the string to lowercase. |
| `upper()` | Converts the string to uppercase. |
| `title()` | Converts the string to title case. |
| `strip()` | Removes leading and trailing whitespace from the string. |
| `words(index, delimiter=" ")` | Splits the string into words and returns the word at the specified index. The `delimiter` parameter specifies the character used to split the string (default is a space). |
| `replace(old, new)` | Replaces all occurrences of `old` with `new` in the string. |
| `remove_accents()` | Removes accents from characters in the string. |

??? example "Example: Using Filters"
    ```csv title="CSV file"
    id,username,repo
    user1,user1,user1-repo
    user2,user2,user2-repo
    ```

    | Field | Pattern | Result |
    |-------|---------|--------|
    | `id` | `{f0.upper()}` | `USER1` |
    | `repo` | `{f2.replace('-', '_')}` | `user1_repo` |

    === "CLI options"
        ```bash
        ghot user invite \
            --pattern-id "{f0.upper()}" \
            --pattern-repo "{f2.replace('-', '_')}" \
            my-org users.csv
        ```

    === "Config"
        ```bash
        ghot config csv.pattern.id "{f0.upper()}"
        ghot config csv.pattern.repo "{f2.replace('-', '_')}"
        ghot user invite my-org users.csv
        ```

??? example "Example: More complex filters"
    ```csv title="CSV file"
    name,surname,username
    fizz,buzz bazz,fizzbuzz
    ```

    | Field | Pattern | Result |
    |-------|---------|--------|
    | `id` | `{f0.lower()}.{f1.words(0).lower()}` | `fizz.buzz` |
    | `username` | `{f2}` | `fizzbuzz` |
    | `repo` | `{f1.words(0).title()}{f0.title()}-Repository` | `BuzzFizz-Repository` |
    | `description` | `Repository for {f0.title()} {f1.title()}` | `Repository for Fizz Buzz` |

    === "CLI options"
        ```bash
        ghot user invite \
            --pattern-id "{f0.lower()}.{f1.words(0).lower()}" \
            --pattern-username "{f2}" \
            --pattern-repo "{f1.words(0).title()}{f0.title()}-Repository" \
            --pattern-description "Repository for {f0.title()} {f1.title()}" \
            my-org users.csv
        ```

    === "Config"
        ```bash
        ghot config csv.pattern.id "{f0.lower()}.{f1.words(0).lower()}"
        ghot config csv.pattern.username "{f2}"
        ghot config csv.pattern.repo "{f1.words(0).title()}{f0.title()}-Repository"
        ghot config csv.pattern.description "Repository for {f0.title()} {f1.title()}"
        ghot user invite my-org users.csv
        ```

## Pattern Options
| Config Key | CLI Option | Default Value | Description |
|--------|---------------|-------------|--------|
| `csv.pattern.id` | `--pattern-id` | `{id}` | Pattern for [`id` field][fields]. |
| `csv.pattern.username` | `--pattern-username` | `{username}` | Pattern for [`username` field][fields]. |
| `csv.pattern.repo` | `--pattern-repo` | `{repo}` | Pattern for [`repo` field][fields]. |
| `csv.pattern.description` | `--pattern-description` | `""` | Pattern for [`description` field][fields]. |

[fields]: #fields
