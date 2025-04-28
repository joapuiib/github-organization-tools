---
icon: octicons/key-16
alias: auth
---

# Authentication
GitHub Organization Tools requires authentication to access the GitHub API.


## Personal Access Tokens
GitHub Organization Tools uses [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
to authenticate with the GitHub API.

The scopes required for the token depend on the actions you want
to perform.

### Required Scopes
The following scopes are required for the different available commands:

- [[users]]:
    - `write:org` required to invite users to an organization.
- [[repository]]:
    - `delete_repo` required to delete repositories.

[invite]: invite.md
[delete]: delete.md

### Storing the Token
GitHub Organization Tools can store the token in the system [`keyring`][keyring]
if the user allows it when prompted to do so.

[keyring]: https://pypi.org/project/keyring/

```
Enter your GitHub Personal Access Token: <token>
Save this token for future use? (y/n): y
```


## Checking Authentication
You can check if you are authenticated by running the following command:

```bash
ghot auth check
```

If not authenticated, you will be prompted to enter
your GitHub Personal Access Token.

## Removing the Token
You can remove the token from the keyring by running
the following command:

```bash
ghot auth remove
```

## Printing the Token
You can print the token to the console by running
the following command:

```bash
ghot auth print
```
