---
icon: octicons/key-16
alias: auth
---
*[PAT]: Personal Access Token

# Authentication
GitHub Organization Tools requires authentication to access the GitHub API, which is achieved using [Personal Access Tokens (PAT)][pat].

[pat]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

The application will try to authenticate using `gh`, the [:simple-github: GitHub CLI tool][gh].
If `gh` is not available, you will be prompted to enter your PAT manually.

[gh]: https://cli.github.com/


## Required Scopes
Different commands require different scopes:

| Command         | Required Scope                          | Description                                   |
|-----------------|-----------------------------------------|-----------------------------------------------|
| [[users]]       | `admin:org`                             | Invite or remove users from an organization   |
| [[repository]]  | `delete_repo`                           | Delete repositories                           |



## Storing the Token
When using [:simple-github: GitHub CLI tool][gh], the token is stored automatically by `gh`.

If not, `ghot` can store the token in the system [`keyring`][keyring]
if the user allows it when prompted to do so.

[keyring]: https://pypi.org/project/keyring/

```
Enter your GitHub Personal Access Token: <token>
Save this token for future use? (y/n): y
```


## Logging In
You can log in by running the command:

```bash
ghot auth login
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
