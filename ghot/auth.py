import getpass
import keyring
from keyring.errors import KeyringError, NoKeyringError
import shutil
import subprocess
import logging
from github import Github, Auth

SERVICE_NAME = "github_pat"

logging.basicConfig(format='[auth] %(message)s', level=logging.INFO)

class AuthManager:
    def __init__(self, init=False):
        self.system_user = getpass.getuser()
        self.token = None
        self.gh_available = shutil.which("gh") is not None
        self.keyring_available = self._check_keyring_available()

        self._load_token()
        if init and not self.token:
            self.login()

    def method(self):
        if self.gh_available:
            return "GitHub CLI"
        elif self.keyring_available:
            return "Keyring"
        else:
            return "None"

    def username(self):
        if not self.token:
            return None
        return self.client().get_user().login

    def _check_keyring_available(self) -> bool:
        """Return True if a usable keyring backend is available."""
        try:
            kr = keyring.get_keyring()
            # Try a tiny test operation
            test_service, test_user = "__keyring_test__", "__keyring_user__"
            keyring.set_password(test_service, test_user, "x")
            keyring.delete_password(test_service, test_user)
            return True
        except (KeyringError, NoKeyringError, RuntimeError):
            return False

    def _load_token(self):
        if self.gh_available:
            try:
                self.token = subprocess.check_output(
                    ["gh", "auth", "token"],
                    stderr=subprocess.DEVNULL,
                ).decode("utf-8").strip()
                return
            except subprocess.CalledProcessError:
                pass  # Not authenticated via gh CLI

        if self.keyring_available:
            logging.info("GitHub CLI not found. Checking keyring for stored token...")
            self.token = keyring.get_password(SERVICE_NAME, self.system_user)
        else:
            logging.warning("No keyring backend available. Cannot retrieve stored token.")


    def login(self):
        if self.token:
            return

        if self.gh_available:
            try:
                logging.info("Using GitHub CLI to authenticate...")
                subprocess.run([
                    "gh", "auth", "login",
                    "--scopes", "repo,read:org,gist,workflow,admin:org,delete_repo",
                    "--git-protocol", "https",
                    "--web",
                ], check=True)
                self._load_token()
                return
            except subprocess.CalledProcessError:
                print("GitHub CLI authentication failed")

        if self.keyring_available:
            self.token = getpass.getpass("Enter your GitHub Personal Access Token: ").strip()
            if input("Save this token for future use? (y/n): ").strip().lower() == 'y':
                keyring.set_password(SERVICE_NAME, self.system_user, self.token)


    def has_token(self):
        return self.token is not None


    def client(self):
        if not self.token:
            return None

        auth = Auth.Token(self.token)
        return Github(auth=auth)


    def print_token(self):
        if not self.token:
            print("No token found.")
            return

        print(f"Token for user '{self.system_user}': {self.token}")


    def remove_token(self):
        if not self.has_token():
            print("No token found.")
            return

        response = input("Are you sure you want to remove the stored key? (y/N): ")
        if response.lower() != "y":
            print("Aborted.")
            return

        if self.gh_available:
            try:
                subprocess.run(["gh", "auth", "logout"], check=True)
                logging.info("Logged out via GitHub CLI.")
                return
            except subprocess.CalledProcessError:
                print("GitHub CLI logout failed or not authenticated via gh CLI.")

        if self.keyring_available:
            keyring.delete_password(SERVICE_NAME, self.system_user)
            print(f"Removed token for user '{self.system_user}'.")
