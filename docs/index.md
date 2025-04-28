---
title: Home
hide:
    - navigation
---
# GitHub Organization Tools

__GitHub Organization Tools (`ghot`)__ is a CLI tool designed to simplify the management of users and repositories
within a GitHub organization.

__Features__:

- [Invite][user-invite] and [remove][user-remove] users from your organization.
- [Create][repo-create], [clone][repo-clone], [pull][repo-pull] or [delete][repo-delete] repositories.
- [Create issues][issue-create] to multiple repositories.

[user-invite]: reference/commands/users.md#inviting-users
[user-remove]: reference/commands/users.md#removing-users
[repo-create]: reference/commands/repositories.md#creating-repositories
[repo-clone]: reference/commands/repositories.md#cloning-repositories
[repo-pull]: reference/commands/repositories.md#pulling-repositories
[repo-delete]: reference/commands/repositories.md#deleting-repositories
[issue-create]: reference/commands/repositories.md#creating-issues

## Installation
This tool can be installed via `pip`:

```bash
pip install ghot
```

## Quick Start Example
- Create a new [:octicons-organization-16: organization][org] in :simple-github: GitHub.

[org]: https://docs.github.com/articles/creating-a-new-organization-from-scratch

- Define a CSV file with the users and repositories.
    ```csv
    id,username,repo
    id1,user1,user1-repo
    id2,user2,user2-repo
    ```

    > - `id` is a custom identifier for the user.
    > - `username` is the GitHub username.
    > - `repo` is the repository name in the organization.
    >
    > Check the [[csv]] for more details.

- [Invite users][user-invite] to the organization:
    ```bash
    ghot user invite my-org users.csv
    ```

- Let users accept the invitation and create their repositories — [Or do it for them][repo-create]!
    ```bash
    ghot repo create my-org users.csv
    ghot repo invite my-org users.csv
    ```

- And [clone][repo-clone] the repositories!
    ```bash
    ghot repo clone my-org users.csv
    ```

[user-invite]: reference/commands/users.md#inviting-users
[repo-create]: reference/commands/repositories.md#creating-repositories
[repo-clone]: reference/commands/repositories.md#cloning-repositories
