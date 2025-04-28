---
icon: octicons/repo-24
alias: repository
---

# Repository Operations

GitHub Organization Tools supports basic repository operations within an organization. You can clone, pull updates, or delete repositories in bulk.


## Creating repositories
To create repositories in a GitHub organization, use the following command:

```bash
ghot repo create [--dry] [--public] [--private] <org> <csv>
```

- `<org>`: The name of the GitHub organization.
- `<csv>`: Path to a CSV file listing repositories to create.
- `--dry` *(optional)*: Simulates the creation process without actually creating the repositories. It still checks for the existence of the organization and the repositories.
- `--public` *(optional)*: Creates the repositories as public. By default, repositories are created as private.
- `--private` *(optional)*: Creates the repositories as private. This is the default behavior.

    > Note: You can use either `--public` or `--private`. If both are specified, `--private` will take precedence.

This command uses the following [fields][fields]:

- `repo`: The name of the repository to be created.
- `description`: A description for the repository.

> See [[csv]] for format and options

[fields]: ../options/csv.md#fields

??? example "Usage: Creating Repositories"
    ```bash
    ghot repo create my-org users.csv
    ```

## Cloning repositories
To clone multiple repositories from an organization:

```bash
ghot repo clone [-d|--destination <path>] [--ssh] [--dry] <org> <csv>
```

- `<org>`: The name of the GitHub organization.
- `<csv>`: Path to a CSV file listing repositories to clone.
- `-d`, `--destination` *(optional)*: Directory where the repositories will be cloned. Defaults to the current directory.
- `--dry` *(optional)*: Lists the repositories that would be cloned, without performing any actions.
- `--ssh` *(optional)*: Clones the repositories using SSH instead of HTTPS. This is useful if you have SSH keys set up for authentication.

    > Note: If you use `--ssh`, ensure that your SSH keys are properly configured in your GitHub account and device.

This command uses the following [fields][fields]:

- `id`: Directory where the repository will be cloned.
- `repo`: The name of the repository to be cloned.

> See [[csv]] for format and options

??? example "Usage: Cloning Repositories"
    ```bash
    ghot repo clone -d org-repos my-org users.csv
    ```


## Pulling repositories
To pull the latest changes for a list of previously cloned repositories:

```bash
ghot repo pull [-d|--destination <path>] [--dry] <csv>
```

- `<csv>`: Path to a CSV file listing repositories to pull.
- `-d|--destination` *(optional)*: Directory where the repositories will be cloned. Defaults to the current directory.
- `--dry` *(optional)*: Lists which repositories would be updated, without making any changes.

This command uses the following [fields][fields]:

- `id`: Directory where the repository exists on the device.

> See [[csv]] for format and options

??? example "Usage: Pulling Repositories"
    ```bash
    ghot repo pull -d org-repos my-org users.csv
    ```


## Deleting repositories
To delete repositories from an organization in GitHub, use the following command:

```bash
ghot repo delete [--dry] [-f|--force] <org> <csv>
```

- `<org>`: The name of the GitHub organization.
- `<csv>`: Path to a CSV file listing repositories to delete.
- `--dry` *(optional)*: Shows which repositories would be deleted, without making any changes.
- `-f|--force` *(optional)*: Skips confirmation and deletes the repositories without prompting.

This command uses the following [fields][fields]:

- `repo`: The name of the repository to be deleted.

> See [[csv]] for format and options

??? example "Usage: Deleting Repositories"
    ```bash
    ghot repo delete my-org users.csv
    ```


## Inviting users as collaborators
To invite users to repositories in a GitHub organization, use the following command:

```bash
ghot repo invite [--dry] <org> <csv>
```

- `<org>`: The name of the GitHub organization.
- `<csv>`: Path to a CSV file listing users and repositories.
- `--dry` *(optional)*: Simulates the invitation process without actually sending invitations. It still checks for the existence of the organization and the repositories.

This command uses the following [fields][fields]:

- `username`: The GitHub username of the user to be invited.
- `repo`: The name of the repository to which the user will be invited.

> See [[csv]] for format and options

??? example "Usage: Inviting Users to Repositories"
    ```bash
    ghot repo invite my-org users.csv
    ```

## Creating issues
To create issues in multiple repositories with the same title and body, use the following command:

```bash
ghot repo issue [--dry] <org> <csv> <title> <body>
```

- `<org>`: The name of the GitHub organization.
- `<csv>`: Path to a CSV file listing repositories.
- `<title>`: The title of the issue to be created.
- `<body>`: The body content of the issue to be created.
- `--dry` *(optional)*: Simulates the issue creation process
    without actually creating the issues.
    It still checks for the existence of the organization
    and the repositories.

This command uses the following [fields][fields]:

- `repo`: The name of the repository where the issue will be created.

> See [[csv]] for format and options

??? example "Usage: Creating Issues"
    ```bash
    ghot issue create my-org users.csv "Issue Title" "Issue Body"
    ```
