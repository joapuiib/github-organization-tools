# GitHub Organization Tools

__GitHub Organization Tools (`ghot`)__ is a CLI tool designed to simplify the management of users and repositories
within a GitHub organization.

__Features__:

- Invite and remove users from your organization.
- Create, clone, pull or delete repositories.
- Create issues to multiple repositories.

## Installation
This tool can be installed via `pip`:

```bash
pip install ghot
```

## Quick Start Example
- Create a new [organization][org] in GitHub.

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
    > Check the [documentation](https://joapuiib.github.io/github-organization-tools/) for more details!

- Invite users to the organization:
    ```bash
    ghot user invite my-org users.csv
    ```

- Let users accept the invitation and create their repositories — Or do it for them!
    ```bash
    ghot repo create my-org users.csv
    ghot repo invite my-org users.csv
    ```

- And clone the repositories!
    ```bash
    ghot repo clone my-org users.csv
    ```
