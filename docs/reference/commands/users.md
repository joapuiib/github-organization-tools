---
icon: octicons/people-16
alias: users
---

# Managing Users

GitHub Organization Tools provides commands to invite or remove users from an organization using a CSV file as input.

## Inviting Users

To invite users to a GitHub organization, use the following command:

```bash
ghot user invite [--dry] <org> <csv>
```

- `<org>`: The name of the GitHub organization.
- `<csv>`: Path to a CSV file containing users.
    to be invited.
- `--dry` *(optional)*: Simulates the invitation process without sending invites. It still checks for the existance of the organization and the users.

This command uses the field [`username`][fields]
from the CSV file to invite users to the organization.

> See [[csv]] for format and options

[fields]: ../options/csv.md#fields


??? example "Usage: Inviting Users"
    ```bash
    ghot user invite my-org users.csv
    ```

## Removing Users

To remove users from a GitHub organization, use:

```bash
ghot user remove [--dry] [--force] <org> <csv>
```

- `<org>`: The name of the GitHub organization.
- `<csv>`: Path to a CSV file listing users to be removed.
- `--force` *(optional)*: Skips confirmation and deletes users from the organization without prompting.
- `--dry` *(optional)*: Simulates the removing process without actually removing the users from the organization. It still checks for the existance of the organization and the users.

This command uses the field [`username`][fields]
from the CSV file to invite users to the organization.

> See [[csv]] for format and options

??? example "Usage: Removing Users"
    ```bash
    ghot user remove my-org users.csv
    ```
