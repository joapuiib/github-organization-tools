import re

from colorama import Fore, Style

# https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories
REPO_NAME_RE = re.compile(r'^[A-Za-z0-9._-]{1,100}$')
# Alphanumeric or single hyphens, cannot start or end with a hyphen, max 39 characters
USERNAME_RE = re.compile(r'^(?=.{1,39}$)[A-Za-z0-9]+(-[A-Za-z0-9]+)*$')


def check_user(user):
    """
    Returns the list of warnings for a single user, ignoring duplicates.
    """
    if not user.id:
        return ["Empty id, row will be skipped"]

    warnings = []
    if not user.username:
        warnings.append("Empty username")
    elif not USERNAME_RE.match(user.username):
        warnings.append(f"Invalid GitHub username '{user.username}'")

    if not user.repo:
        warnings.append("Empty repo")
    elif not REPO_NAME_RE.match(user.repo) or user.repo in ('.', '..'):
        warnings.append(f"Invalid repository name '{user.repo}'")

    return warnings


def csv_show(loader, path, sources, ids=None):
    """
    Prints the patterns and the data extracted from each row of the CSV file.
    If ids is given, only the rows with those ids are shown.
    Returns the number of warnings found.
    """
    print(f"CSV file: {path}")
    print("Patterns:")
    for field in ("id", "username", "repo", "description"):
        pattern = getattr(loader, f"pattern_{field}")
        print(f"  {field}: {Fore.CYAN}{pattern!r}{Fore.RESET} {Style.DIM}({sources[field]}){Style.RESET_ALL}")

    total = 0
    total_warnings = 0
    seen_ids = {}
    seen_repos = {}

    for line, row in loader.rows(path):
        label = f"line {line}"

        try:
            user = loader.map(row)
        except Exception as ex:
            if ids:
                continue
            warnings = [f"Could not read row: {ex}"]
            user = None
        else:
            warnings = check_user(user)
            if user.id:
                label = user.id
                if user.id in seen_ids:
                    warnings.append(f"Duplicate id (also on line {seen_ids[user.id]})")
                seen_ids.setdefault(user.id, line)
            if user.id and user.repo:
                repo = user.repo.lower()
                if repo in seen_repos:
                    warnings.append(f"Duplicate repo (also on line {seen_repos[repo]})")
                seen_repos.setdefault(repo, line)

        if ids and user.id not in ids:
            continue

        total += 1
        total_warnings += len(warnings)
        color = Fore.YELLOW if warnings else Fore.GREEN
        details = ""
        if user:
            details = f"username '{user.username}', repo '{user.repo}', description '{user.description}'"
        print(f"{Style.BRIGHT}{color}{label}{Style.RESET_ALL}: {details}")
        for warning in warnings:
            print(f"  {Fore.YELLOW}{warning}.{Fore.RESET}")

    if ids:
        for id in ids:
            if id not in seen_ids:
                total_warnings += 1
                print(f"{Style.BRIGHT}{Fore.YELLOW}{id}{Style.RESET_ALL}: {Fore.YELLOW}Id not found.{Fore.RESET}")

    print(f"Total rows: {total}")
    color = Fore.YELLOW if total_warnings else Fore.GREEN
    print(f"{color}Warnings: {total_warnings}{Fore.RESET}")
    return total_warnings
