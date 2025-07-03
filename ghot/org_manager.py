from colorama import Fore, Style
import git
import os

from github import GithubException
from git.exc import InvalidGitRepositoryError

class OrgManager:
    def __init__(self, gh_client):
        self.gh_client = gh_client

    def _get_org(self, org_name):
        try:
            return self.gh_client.get_organization(org_name)
        except GithubException as e:
            print(f"{Fore.RED}Error retrieving organization '{org_name}': {e}{Fore.RESET}")
            exit(1)

    def _get_repo(self, login, repo):
        prefix = f"{login}/{repo}"
        try:
            return self.gh_client.get_repo(f"{login}/{repo}")
        except GithubException:
            return None

    def _get_user(self, username):
        try:
            return self.gh_client.get_user(username)
        except GithubException:
            return None

    def _unpack_status(self, status):
        msg = status[0]
        color = status[1] if len(status) > 1 else Fore.RESET
        style = status[2] if len(status) > 2 else Style.RESET_ALL
        return msg, color, style

    def _print_status(self, user, status):
        message, color, style = self._unpack_status(status)
        print(f"{Style.BRIGHT}{Fore.GREEN}{user.id}{Style.RESET_ALL}: {style}{color}{message}.{Style.RESET_ALL}")

    def _confirm_action(self, prompt, force):
        return force or self._confirm_prompt(prompt)

    def _confirm_prompt(self, prompt):
        return input(f"{Fore.CYAN}{prompt} (y/N): {Fore.RESET}").strip().lower() == 'y'

    def _repo_dir(self, user, destination=None):
        return os.path.join(destination or '', user.id)


    def _process_users(self, users, process_func, status_map):
        for user in users:
            if not user.is_valid():
                continue

            print(f"{Style.BRIGHT}{Fore.GREEN}{user.id}{Style.RESET_ALL}: ...", end="\r")
            result = process_func(user)
            kwargs = {}
            if isinstance(result, tuple):
                result, kwargs = result

            self._print_status(user, status_map(user, **kwargs)[result])


    def _process_user_invite(self, org, user, members, invitations, dry=False):
        if not user.is_valid():
            return "invalid"

        if not user.username:
            return "no_username"

        username = user.username.lower()
        if username in members:
            return "member"
        elif username in invitations:
            return "already_invited"
        else:
            gh_user = self._get_user(user.username)
            if not gh_user:
                return "user_not_found"

            if dry:
                return "invite_dry"
            else:
                org.invite_user(gh_user, role="direct_member")
                return "invite"



    def user_invite(self, org_name, users, dry=False):
        org = self._get_org(org_name)

        members = [m.login.lower() for m in org.get_members()]
        invitations = [i.login.lower() for i in org.invitations()]
        print(f"Total members: {len(members)}")
        print(f"Pending invitations: {len(invitations)}")

        def process(user):
            return self._process_user_invite(org, user, members, invitations, dry)

        def status_map(user):
            return {
                "no_username": ("No username", Fore.RESET, Style.DIM),
                "user_not_found": (f"User '{user.username}' doesn't exist", Fore.RED),
                "member": (f"User '{user.username}' is already a member", Fore.GREEN),
                "already_invited": (f"User '{user.username}' is already invited", Fore.YELLOW),
                "invite_dry": (f"Invitation sent to '{user.username}' (dry)", Fore.CYAN),
                "invite": (f"Invitation sent to '{user.username}'", Fore.CYAN),
            }
        self._process_users(users, process, status_map)


    def _process_user_remove(self, org, user, members, invitations, dry=False, force=False):
        if not user.is_valid():
            return "invalid"

        if not user.username:
            return "no_username"

        gh_user = self._get_user(user.username)
        if not gh_user:
            return "user_not_found"

        username = user.username.lower()
        if username in invitations:
            if not self._confirm_action(f"{user.id}: Are you sure you want to cancel '{user.username}' invitation?", force):
                return "deletion_skipped"

            if dry:
                return "invite_removed_dry"
            else:
                invite = invitations[username]
                self.gh_client._Github__requester.requestJsonAndCheck(
                    "DELETE",
                    f"{org.url}/invitations/{invite.id}"
                )
                return "invite_removed"

        if username not in members:
            return "not_member"

        if not self._confirm_action(f"{user.id}: Are you sure you want to remove '{user.username}'?", force):
            return "deletion_skipped"

        if dry:
            return "removed_dry"
        else:
            org.remove_from_members(gh_user)
            return "removed"


    def user_remove(self, org_name, users, dry=False, force=False):
        org = self._get_org(org_name)

        members = [m.login.lower() for m in org.get_members()]
        invitations = {i.login.lower() : i for i in org.invitations()}

        print(f"Total members: {len(members)}")
        print(f"Pending invitations: {len(invitations)}")

        def process(user):
            return self._process_user_remove(org, user, members, invitations, dry, force)

        def status_map(user):
            return {
                "invalid": ("Invalid user", Fore.RED),
                "no_username": ("No username", Fore.RESET, Style.DIM),
                "user_not_found": (f"User '{user.username}' doesn't exist", Fore.RED),
                "not_member": (f"User '{user.username}' is not a organization member", Fore.RED),
                "invite_removed_dry": (f"Invitation for '{user.username}' removed (dry)", Fore.YELLOW),
                "invite_removed": (f"Invitation for '{user.username}' removed", Fore.YELLOW),
                "deletion_skipped": ("Deletion skipped", Fore.RESET, Style.DIM),
                "removed_dry": (f"User '{user.username}' removed from organization (dry)", Fore.CYAN),
                "removed": (f"User '{user.username}' removed from organization", Fore.CYAN),
            }
        self._process_users(users, process, status_map)


    def _process_repo_create(self, org, user, dry=False, private=True):
        if not user.is_valid():
            return "invalid"

        if not user.repo:
            return "no_repo"

        repo = self._get_repo(org.login, user.repo)
        if repo:
            return "repo_exists"

        if dry:
            return "repo_created_dry"
        else:
            org.create_repo(
                name=user.repo,
                private=private,
                description=user.description,
                auto_init=False,
            )
            return "repo_created"


    def repo_create(self, org_name, users, dry=False, private=True):
        org = self._get_org(org_name)

        def process(user):
            return self._process_repo_create(org, user, dry, private)

        def status_map(user):
            visibility = "private" if private else "public"
            return {
                "invalid": ("Invalid user", Fore.RED),
                "no_repo": (f"No repository name", Fore.RESET, Style.DIM),
                "repo_exists": (f"Repository '{org_name}/{user.repo}' already exists", Fore.GREEN),
                "repo_created_dry": (f"Repository '{org_name}/{user.repo}' created ({visibility}) (dry)", Fore.CYAN),
                "repo_created": (f"Repository '{org_name}/{user.repo}' created ({visibility})", Fore.CYAN),
            }
        self._process_users(users, process, status_map)


    def _process_repo_invite(self, org, user, org_members, dry=False):
        if not user.is_valid():
            return "invalid"

        if not user.username:
            return "no_username"

        if not user.repo:
            return "no_repo"

        gh_user = self._get_user(user.username)
        if not gh_user:
            return "user_not_found"

        username = user.username.lower()
        if not username in org_members:
            return "no_org_member"

        repo = self._get_repo(org.login, user.repo)
        if not repo:
            return "repo_not_found"
        repo_collaborators = [c.login for c in repo.get_collaborators()]
        invitations = [i.invitee.login for i in repo.get_pending_invitations()]

        if username in repo_collaborators:
            return "already_collaborator"

        if username in invitations:
            return "already_invited"

        if dry:
            return "invite_dry"
        else:
            repo.add_to_collaborators(gh_user, permission="push")
            return "invite"


    # Check user is in the organization
    def repo_invite(self, org, users, dry=False):
        org = self._get_org(org)

        org_members = [m.login.lower() for m in org.get_members()]

        def process(user):
            return self._process_repo_invite(org, user, org_members, dry=dry)

        def status_map(user):
            return {
                "invalid": ("Invalid user", Fore.RED),
                "no_username": ("No username", Fore.RESET, Style.DIM),
                "user_not_found": (f"User '{user.username}' doesn't exist", Fore.RED),
                "no_org_member": (f"User '{user.username}' is not a member of the organization", Fore.RED),
                "no_repo": (f"No repository name", Fore.RESET, Style.DIM),
                "repo_not_found": (f"Repository '{user.repo}' not found", Fore.RED),
                "already_collaborator": (f"User '{user.username}' is already a collaborator of repository '{user.repo}'", Fore.GREEN),
                "already_invited": (f"User '{user.username}' is already invited to repository '{user.repo}'", Fore.YELLOW),
                "invite_dry": (f"User '{user.username}' invited to repository '{user.repo}' (dry)", Fore.CYAN),
                "invite": (f"User '{user.username}' invited to repository '{user.repo}'", Fore.CYAN),
            }
        self._process_users(users, process, status_map)


    def _process_repo_clone(self, org, user, destination=None, dry=False, ssh=False):
        if not user.is_valid():
            return "invalid"

        repo_dir = user.id
        if destination:
            repo_dir = os.path.join(destination, repo_dir)

        if not user.repo:
            return "no_repo"

        if os.path.isdir(repo_dir):
            try:
                repo = git.Repo(repo_dir)
                return "repo_already_cloned"
            except InvalidGitRepositoryError:
                return "exists_but_not_repo"

        repo = self._get_repo(org.login, user.repo)
        if not repo:
            return "repo_not_found"

        clone_url = repo.ssh_url if ssh else repo.clone_url

        if dry:
            return "repo_cloned_dry"
        else:
            git.Repo.clone_from(clone_url, repo_dir)
            return "repo_cloned"


    def repo_clone(self, org_name, users, destination=None, dry=False, ssh=False):
        org = self._get_org(org_name)

        def process(user):
            return self._process_repo_clone(org, user, destination, dry, ssh)

        def status_map(user):
            repo_dir = user.id
            if destination:
                repo_dir = os.path.join(destination, repo_dir)
            protocol = "SSH" if ssh else "HTTPS"
            return {
                "invalid": ("Invalid user", Fore.RED),
                "no_repo": ("No repository name", Fore.RESET, Style.DIM),
                "repo_already_cloned": (f"Repository '{org_name}/{user.repo}' already cloned on '{repo_dir}'", Fore.GREEN),
                "exists_but_not_repo": (f"Directory '{repo_dir}' exists but is not a git repository", Fore.RED),
                "repo_cloned": (f"Repository '{org_name}/{user.repo}' cloned on '{repo_dir}' ({protocol})", Fore.CYAN),
                "repo_cloned_dry": (f"Repository '{org_name}/{user.repo}' cloned on '{repo_dir}' ({protocol}) (dry)", Fore.CYAN),
                "repo_not_found": (f"Repository '{org_name}/{user.repo}' not found", Fore.RED),
            }
        self._process_users(users, process, status_map)


    def _process_repo_pull(self, user, destination=None, dry=False):
        if not user.is_valid():
            return "invalid"

        repo_dir = user.id
        if destination:
            repo_dir = os.path.join(destination, repo_dir)

        if not user.repo:
            return "no_repo"

        if not os.path.isdir(repo_dir):
            return "repo_not_cloned"

        if dry:
            return "repo_pull_dry"

        try:
            repo = git.Repo(repo_dir)
            o = repo.remotes.origin
            o.fetch()

            # get default branch from origin/HEAD
            default_ref = repo.git.symbolic_ref('refs/remotes/origin/HEAD')
            default_branch = default_ref.rsplit('/', 1)[-1]

            # checkout default branch and reset to origin
            repo.git.checkout(default_branch)
            repo.git.reset("--hard", f"origin/{repo.active_branch}")

            return "repo_pull"
        except Exception as ex:
            return "error_pulling"


    def repo_pull(self, users, destination=None, dry=False):
        def process(user):
            return self._process_repo_pull(user, destination, dry)

        def status_map(user):
            repo_dir = user.id
            if destination:
                repo_dir = os.path.join(destination, repo_dir)
            return {
                "invalid": ("Invalid user", Fore.RED),
                "no_repo": ("No repository name", Fore.RESET, Style.DIM),
                "repo_not_cloned": (f"Repository '{user.repo}' not cloned on '{repo_dir}'", Fore.YELLOW),
                "repo_pull": (f"Repository '{user.repo}' pulled on '{repo_dir}'", Fore.CYAN),
                "repo_pull_dry": (f"Repository '{user.repo}' pulled on '{repo_dir}' (dry)", Fore.CYAN),
                "error_pulling": (f"Error pulling repository '{user.repo}' on '{repo_dir}'", Fore.RED),
            }
        self._process_users(users, process, status_map)


    def _process_repo_delete(self, org, user, force=False, dry=False):
        if not user.is_valid():
            return "invalid"

        if not user.repo:
            return "no_repo"

        repo = self._get_repo(org.login, user.repo)
        if not repo:
            return "repo_not_found"

        repo_id = f"{org.login}/{user.repo}"
        if not self._confirm_action(f"{user.id}: Are you sure you want to delete '{repo_id}'?", force):
            return "deletion_skipped"

        if dry:
            return "deleted_dry"
        else:
            repo.delete()
            return "deleted"


    def repo_delete(self, org_name, users, force=False, dry=False):
        org = self._get_org(org_name)

        def process(user):
            return self._process_repo_delete(org, user, force, dry)

        def status_map(user):
            return {
                "invalid": ("Invalid user", Fore.RED),
                "no_repo": ("No repository name", Fore.RESET, Style.DIM),
                "repo_not_found": (f"Repository '{org_name}/{user.repo}' not found", Fore.RED),
                "deletion_skipped": (f"Deletion skipped", Fore.RESET, Style.DIM),
                "deleted_dry": (f"Repository '{org_name}/{user.repo}' deleted (dry)", Fore.CYAN),
                "deleted": (f"Repository '{org_name}/{user.repo}' deleted", Fore.CYAN),
            }
        self._process_users(users, process, status_map)


    def _process_issue_create(self, org, user, title, body, dry=False):
        if not user.is_valid():
            return "invalid"

        if not user.repo:
            return "no_repo"

        if not title:
            return "no_title"

        if not body:
            return "no_body"

        repo = self._get_repo(org.login, user.repo)
        if not repo:
            return "repo_not_found"

        if dry:
            return "issue_created_dry"
        else:
            body = body.replace("\\n", "\n")
            issue = repo.create_issue(title, body)
            return "issue_created", {"number": issue.number}


    def issue_create(self, org_name, users, title, body, dry=False):
        org = self._get_org(org_name)

        def process(user):
            return self._process_issue_create(org, user, title, body, dry)

        def status_map(user, **kwargs):
            return {
                "invalid": ("Invalid user", Fore.RED),
                "no_repo": ("No repository name", Fore.RESET, Style.DIM),
                "no_title": ("No issue title", Fore.RESET, Style.DIM),
                "no_body": ("No issue body", Fore.RESET, Style.DIM),
                "repo_not_found": (f"Repository '{org_name}/{user.repo}' not found", Fore.RED),
                "issue_created_dry": (f"Issue created on '{org_name}/{user.repo}' (dry)", Fore.CYAN),
                "issue_created": (f"Issue created on '{org_name}/{user.repo}' (#{kwargs.get('number')})", Fore.CYAN),
            }
        self._process_users(users, process, status_map)
