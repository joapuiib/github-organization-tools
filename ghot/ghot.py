import argparse
import sys

from .auth import AuthManager
from .config import load_config, apply_config_defaults, write_config, show_config
from .csv_loader import CSVUserLoader
from .csv_show import csv_show
from .org_manager import OrgManager

__version__ = "0.3.0"

PATTERN_DEFAULTS = {
    'id': '{f0}',
    'username': '{f1}',
    'repo': '{f2}',
    'description': '',
}


class StorePattern(argparse.Action):
    """
    Stores the value and records that the pattern was given on the command line.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        cli_patterns = getattr(namespace, 'cli_patterns', set())
        namespace.cli_patterns = cli_patterns | {self.dest}


def build_parser():
    config = load_config()
    def add_csv_options(parser):
        parser.add_argument('csv', help='CSV file')
        parser.add_argument('--id', dest='ids', action='append', metavar='ID',
                            help='Only process the user with this id (can be repeated)')
        parser.add_argument('--pattern-id', action=StorePattern, default=PATTERN_DEFAULTS['id'], help='Pattern for user ID')
        parser.add_argument('--pattern-username', action=StorePattern, default=PATTERN_DEFAULTS['username'], help='Pattern for username')
        parser.add_argument('--pattern-repo', action=StorePattern, default=PATTERN_DEFAULTS['repo'], help='Pattern for repository name')
        parser.add_argument('--pattern-description', action=StorePattern, default=PATTERN_DEFAULTS['description'], help='Pattern for repository description')
        apply_config_defaults(parser, config)

    def add_dry_option(parser):
        parser.add_argument('--dry', action='store_true', help='Dry run mode')

    def add_concurrency_options(parser):
        parser.add_argument('-j', '--workers', type=int, default=8,
                            help='Number of parallel workers (default: 8, use 1 for sequential)')
        parser.add_argument('--no-progress', action='store_true',
                            help='Disable live progress display')

    parser = argparse.ArgumentParser(description='GitHub Organization Tools.')
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')
    commands = parser.add_subparsers(title="commands", dest="commands", metavar="<command>")

    # ghot auth
    auth_p = commands.add_parser('auth', help='Manage GitHub authentication', description='Manage GitHub authentication.')
    auth_p.set_defaults(group_parser=auth_p)
    auth_commands = auth_p.add_subparsers(title="commands", dest="auth_commands", metavar="<command>")
    ## ghot auth check|login|print|remove
    auth_commands.add_parser('check', help='Check if you are authenticated', description='Check if you are authenticated.')
    auth_commands.add_parser('login', help='Log in and store the GitHub token', description='Log in and store the GitHub token.')
    auth_commands.add_parser('remove', help='Remove the stored GitHub token', description='Remove the stored GitHub token.')
    auth_commands.add_parser('print', help='Print the GitHub token', description='Print the GitHub token.')

    # ghot config
    config_p = commands.add_parser('config', help='Set or show configuration values', description='Set or show configuration values.')
    config_p.set_defaults(group_parser=config_p)
    config_commands = config_p.add_subparsers(title="commands", dest="config_commands", metavar="<command>")
    ## ghot config [set] [--global] <key> <value>
    config_set_p = config_commands.add_parser('set', help='Set a configuration value', description='Set a configuration value.')
    config_set_p.add_argument('--global', dest="_global", action='store_true', help='Set the config globally')
    config_set_p.add_argument('key', help='Config key to set')
    config_set_p.add_argument('value', help='Config value to set')
    ## ghot config show <key>
    config_show_p = config_commands.add_parser('show', help='Show configuration values', description='Show configuration values.')
    config_show_p.add_argument('key', help='Config key to show', nargs='?', default=None)

    # ghot csv
    csv_p = commands.add_parser('csv', help='Inspect how the CSV file is read', description='Inspect how the CSV file is read.')
    csv_p.set_defaults(group_parser=csv_p)
    csv_commands = csv_p.add_subparsers(title="commands", dest="csv_commands", metavar="<command>")
    ## ghot csv show <csv>
    csv_show_p = csv_commands.add_parser('show', help='Show the data read from the CSV file and check for problems', description='Show the data read from the CSV file and check for problems.')
    add_csv_options(csv_show_p)

    # ghot user
    user_p = commands.add_parser('user', help='Manage organization members', description='Manage organization members.')
    user_p.set_defaults(group_parser=user_p)
    user_commands = user_p.add_subparsers(title="commands", dest="user_commands", metavar="<command>")
    ## ghot user invite <org> <csv>
    user_invite_p = user_commands.add_parser('invite', help='Invite users to the organization', description='Invite users to the organization.')
    user_invite_p.add_argument("org", help='Organization name')
    add_csv_options(user_invite_p)
    add_concurrency_options(user_invite_p)
    add_dry_option(user_invite_p)
    ## ghot user remove <org> <csv> [-f|--force]
    user_remove_p = user_commands.add_parser('remove', help='Remove users from the organization', description='Remove users from the organization.')
    user_remove_p.add_argument("org", help='Organization name')
    add_csv_options(user_remove_p)
    add_concurrency_options(user_remove_p)
    add_dry_option(user_remove_p)
    user_remove_p.add_argument("-f", "--force", action="store_true", default=False, help='Force removal')

    # ghot repo
    repo_p = commands.add_parser('repo', help='Manage organization repositories', description='Manage organization repositories.')
    repo_p.set_defaults(group_parser=repo_p)
    repo_commands = repo_p.add_subparsers(title="commands", dest="repo_commands", metavar="<command>")
    ## ghot repo create [--public] [--private] <org> <csv>
    repo_create_p = repo_commands.add_parser('create', help='Create a repository for each user', description='Create a repository for each user.')
    repo_create_p.add_argument("org", help='Organization name')
    add_csv_options(repo_create_p)
    add_concurrency_options(repo_create_p)
    add_dry_option(repo_create_p)
    repo_create_p.add_argument('--public', action='store_true', help='Create public repositories')
    repo_create_p.add_argument('--private', action='store_true', help='Create private repositories')
    repo_create_p.add_argument('--username-only', action='store_true', help='Create repositories for entries that have specified an username')
    ## ghot repo clone [-d|--destination <path>] <csv>
    repo_clone_p = repo_commands.add_parser('clone', help="Clone each user's repository", description="Clone each user's repository.")
    repo_clone_p.add_argument("org", help='Organization name')
    add_csv_options(repo_clone_p)
    add_concurrency_options(repo_clone_p)
    add_dry_option(repo_clone_p)
    repo_clone_p.add_argument('-d', '--destination', help='Destination directory where the repositoiry will be cloned')
    repo_clone_p.add_argument('--ssh', action='store_true', help='Use SSH for cloning')
    ## ghot repo pull [-d|--destination <path>] <csv>
    repo_pull_p = repo_commands.add_parser('pull', help='Pull each cloned repository', description='Pull each cloned repository.')
    add_csv_options(repo_pull_p)
    add_concurrency_options(repo_pull_p)
    add_dry_option(repo_pull_p)
    repo_pull_p.add_argument('-d', '--destination', help='Destination directory where the repositoiry will be pulled')
    ## ghot repo delete [-f|--force] <org> <csv>
    repo_delete_p = repo_commands.add_parser('delete', help="Delete each user's repository", description="Delete each user's repository.")
    repo_delete_p.add_argument('org', help='Organization name')
    add_csv_options(repo_delete_p)
    add_concurrency_options(repo_delete_p)
    add_dry_option(repo_delete_p)
    repo_delete_p.add_argument('-f', '--force', action='store_true', default=False, help='Force deletion')
    ## ghot repo invite <org> <csv>
    repo_invite_p = repo_commands.add_parser('invite', help='Invite each user as a collaborator to their repository', description='Invite each user as a collaborator to their repository.')
    repo_invite_p.add_argument('org', help='Organization name')
    add_csv_options(repo_invite_p)
    add_concurrency_options(repo_invite_p)
    add_dry_option(repo_invite_p)

    # ghot issue
    issue_p = commands.add_parser('issue', help='Manage repository issues', description='Manage repository issues.')
    issue_p.set_defaults(group_parser=issue_p)
    issue_commands = issue_p.add_subparsers(title="commands", dest="issue_commands", metavar="<command>")
    ## ghot issue create <org> <csv> <title> <body>
    issue_create_p = issue_commands.add_parser('create', help="Create an issue in each user's repository", description="Create an issue in each user's repository.")
    issue_create_p.add_argument('org', help='Organization name')
    add_csv_options(issue_create_p)
    add_concurrency_options(issue_create_p)
    issue_create_p.add_argument('title', help='Issue title')
    issue_create_p.add_argument('body', help='Issue body')
    add_dry_option(issue_create_p)

    return parser


def preprocess_args(argv):
    if len(argv) > 2:
        if argv[1] == "config" and argv[2] not in ["set", "show", "-h", "--help"]:
            argv.insert(2, "set")

    return argv


def handle_config(args):
    match args.config_commands:
        case "set":
            write_config(args.key, args.value, global_scope=args._global)
        case "show":
            show_config(args.key)


def handle_csv(args):
    match args.csv_commands:
        case "show":
            config = load_config()
            cli_patterns = getattr(args, 'cli_patterns', set())
            sources = {}
            for field in PATTERN_DEFAULTS:
                if f"pattern_{field}" in cli_patterns:
                    sources[field] = "cli"
                elif config.has_option('csv', f"pattern.{field}"):
                    sources[field] = "config"
                else:
                    sources[field] = "default"

            warnings = csv_show(csv_loader(args), args.csv, sources, ids=args.ids)
            if warnings:
                sys.exit(1)


def handle_auth(args):
    auth = AuthManager()
    match args.auth_commands:
        case "check":
            if auth.has_token():
                print(f"Authenticated as {auth.username()} via {auth.method()}")
            else:
                print("Not authenticated")
        case "login":
            if auth.has_token():
                print(f"Already authenticated as {auth.username()} via {auth.method()}")
                return
            auth.login()
        case "print":
            auth.print_token()
        case "remove":
            auth.remove_token()


def handle_user(args):
    org_manager = init_org_manager(args)
    users = load_users(args)

    match args.user_commands:
        case "invite":
            org_manager.user_invite(args.org, users, dry=args.dry)
        case "remove":
            org_manager.user_remove(args.org, users, dry=args.dry, force=args.force)


def handle_repo(args):
    org_manager = init_org_manager(args)
    users = load_users(args)

    match args.repo_commands:
        case "create":
            private = True
            if args.public and not args.private:
                private = False

            org_manager.repo_create(args.org, users, private=private, dry=args.dry, username_only=args.username_only)

        case "clone":
            org_manager.repo_clone(args.org, users, destination=args.destination, dry=args.dry, ssh=args.ssh)
        case "pull":
            org_manager.repo_pull(users, destination=args.destination, dry=args.dry)
        case "delete":
            org_manager.repo_delete(args.org, users, dry=args.dry, force=args.force)
        case "invite":
            org_manager.repo_invite(args.org, users, dry=args.dry)


def handle_issue(args):
    org_manager = init_org_manager(args)
    users = load_users(args)

    match args.issue_commands:
        case "create":
            org_manager.issue_create(args.org, users, args.title, args.body, dry=args.dry)


def init_org_manager(args):
    auth = AuthManager(init=True)
    workers = getattr(args, 'workers', 8)
    progress = not getattr(args, 'no_progress', False)
    org_manager = OrgManager(auth.client(), workers=workers, progress=progress)
    return org_manager


def csv_loader(args):
    return CSVUserLoader(
        pattern_id=args.pattern_id,
        pattern_username=args.pattern_username,
        pattern_repo=args.pattern_repo,
        pattern_description=args.pattern_description,
    )


def load_users(args):
    users = csv_loader(args).load(args.csv)
    if args.ids:
        found = {user.id for user in users}
        missing = [id for id in args.ids if id not in found]
        if missing:
            sys.exit(f"Id not found in {args.csv}: {', '.join(missing)}")
        users = [user for user in users if user.id in args.ids]
    return users


def main():
    sys.argv = preprocess_args(sys.argv)
    parser = build_parser()
    args = parser.parse_args()

    if args.commands is None:
        parser.print_help()
        return
    if getattr(args, f"{args.commands}_commands") is None:
        args.group_parser.print_help()
        return

    try:
        match args.commands:
            case "auth":
                handle_auth(args)
            case "config":
                handle_config(args)
            case "csv":
                handle_csv(args)
            case "user":
                handle_user(args)
            case "repo":
                handle_repo(args)
            case "issue":
                handle_issue(args)

    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except ValueError as e:
        # print on stderr
        print(e, file=sys.stderr)
