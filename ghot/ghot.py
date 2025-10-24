import argparse
import sys

from .auth import AuthManager
from .config import load_config, apply_config_defaults, write_config, show_config
from .csv_loader import CSVUserLoader
from .org_manager import OrgManager

__version__ = "0.2.0"

def build_parser():
    config = load_config()
    def add_csv_options(parser):
        parser.add_argument('csv', help='CSV file')
        parser.add_argument('--pattern-id', default='{f0}', help='Pattern for user ID')
        parser.add_argument('--pattern-username', default='{f1}', help='Pattern for username')
        parser.add_argument('--pattern-repo', default='{f2}', help='Pattern for repository name')
        parser.add_argument('--pattern-description', default='', help='Pattern for repository description')
        apply_config_defaults(parser, config)

    def add_dry_option(parser):
        parser.add_argument('--dry', action='store_true', help='Dry run mode')

    parser = argparse.ArgumentParser(description='Git tools.')
    commands = parser.add_subparsers(title="commands", dest="commands")

    # ghot auth
    auth_p = commands.add_parser('auth')
    ## ghot auth check|print|remove
    auth_p.add_argument('auth_commands', choices=['check', 'login', 'remove', 'print'], help='Authentication command')

    # ghot config
    config_p = commands.add_parser('config')
    config_commands = config_p.add_subparsers(title="config_commands", dest="config_commands", required=True)
    ## ghot config [set] [--global] <key> <value>
    config_set_p = config_commands.add_parser('set')
    config_set_p.add_argument('--global', dest="_global", action='store_true', help='Set the config globally')
    config_set_p.add_argument('key', help='Config key to set')
    config_set_p.add_argument('value', help='Config value to set')
    ## ghot config show <key>
    config_show_p = config_commands.add_parser('show')
    config_show_p.add_argument('key', help='Config key to show', nargs='?', default=None)

    # ghot user
    user_p = commands.add_parser('user')
    user_commands = user_p.add_subparsers(title="user_commands", dest="user_commands", required=True)
    ## ghot user invite <org> <csv>
    user_invite_p = user_commands.add_parser('invite')
    user_invite_p.add_argument("org", help='Organization name')
    add_csv_options(user_invite_p)
    add_dry_option(user_invite_p)
    ## ghot user remove <org> <csv> [-f|--force]
    user_remove_p = user_commands.add_parser('remove')
    user_remove_p.add_argument("org", help='Organization name')
    add_csv_options(user_remove_p)
    add_dry_option(user_remove_p)
    user_remove_p.add_argument("-f", "--force", action="store_true", default=False, help='Force removal')

    # ghot repo
    repo_p = commands.add_parser('repo')
    repo_commands = repo_p.add_subparsers(title="repo_commands", dest="repo_commands", required=True)
    ## ghot repo create [--public] [--private] <org> <csv>
    repo_create_p = repo_commands.add_parser('create')
    repo_create_p.add_argument("org", help='Organization name')
    add_csv_options(repo_create_p)
    add_dry_option(repo_create_p)
    repo_create_p.add_argument('--public', action='store_true', help='Create public repositories')
    repo_create_p.add_argument('--private', action='store_true', help='Create private repositories')
    repo_create_p.add_argument('--username-only', action='store_true', help='Create repositories for entries that have specified an username')
    ## ghot repo clone [-d|--destination <path>] <csv>
    repo_clone_p = repo_commands.add_parser('clone')
    repo_clone_p.add_argument("org", help='Organization name')
    add_csv_options(repo_clone_p)
    add_dry_option(repo_clone_p)
    repo_clone_p.add_argument('-d', '--destination', help='Destination directory where the repositoiry will be cloned')
    repo_clone_p.add_argument('--ssh', action='store_true', help='Use SSH for cloning')
    ## ghot repo pull [-d|--destination <path>] <csv>
    repo_pull_p = repo_commands.add_parser('pull')
    add_csv_options(repo_pull_p)
    add_dry_option(repo_pull_p)
    repo_pull_p.add_argument('-d', '--destination', help='Destination directory where the repositoiry will be pulled')
    ## ghot repo delete [-f|--force] <org> <csv>
    repo_delete_p = repo_commands.add_parser('delete')
    repo_delete_p.add_argument('org', help='Organization name')
    add_csv_options(repo_delete_p)
    add_dry_option(repo_delete_p)
    repo_delete_p.add_argument('-f', '--force', action='store_true', default=False, help='Force deletion')
    ## ghot repo invite <org> <csv>
    repo_invite_p = repo_commands.add_parser('invite')
    repo_invite_p.add_argument('org', help='Organization name')
    add_csv_options(repo_invite_p)
    add_dry_option(repo_invite_p)

    # ghot issue
    issue_p = commands.add_parser('issue')
    issue_commands = issue_p.add_subparsers(title="issue_commands", dest="issue_commands", required=True)
    ## ghot issue create <org> <csv> <title> <body>
    issue_create_p = issue_commands.add_parser('create')
    issue_create_p.add_argument('org', help='Organization name')
    add_csv_options(issue_create_p)
    issue_create_p.add_argument('title', help='Issue title')
    issue_create_p.add_argument('body', help='Issue body')
    add_dry_option(issue_create_p)

    return parser


def preprocess_args(argv):
    if len(argv) > 2:
        if argv[1] == "config" and argv[2] not in ["set", "show"]:
            argv.insert(2, "set")

    return argv


def handle_config(args):
    # Default config action
    if args.config_commands is None:
        args.config_commands = "set"

    match args.config_commands:
        case "set":
            write_config(args.key, args.value, global_scope=args._global)
        case "show":
            show_config(args.key)


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
    org_manager = OrgManager(auth.client())
    return org_manager


def load_users(args):
    csv_loader = CSVUserLoader(
        pattern_id=args.pattern_id,
        pattern_username=args.pattern_username,
        pattern_repo=args.pattern_repo,
        pattern_description=args.pattern_description,
    )
    users = csv_loader.load(args.csv)
    return users


def main():
    sys.argv = preprocess_args(sys.argv)
    parser = build_parser()
    args = parser.parse_args()

    args = parser.parse_args()

    try:
        match args.commands:
            case "auth":
                handle_auth(args)
            case "config":
                handle_config(args)
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
