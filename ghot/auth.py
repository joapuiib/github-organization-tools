import getpass
import keyring
import shutil
import subprocess
from github import Github, Auth

SERVICE_NAME = "github_pat"

class AuthManager:
    def __init__(self):
        self.system_user = getpass.getuser()
        self.token = None
        self.gh_available = shutil.which("gh") is not None
        self._load_token()


    def _load_token(self):
        if self.gh_available:
            try:
                self.token = subprocess.check_output(["gh", "auth", "token"]).decode("utf-8").strip()
                return
            except subprocess.CalledProcessError:
                pass  # Not authenticated via gh CLI

        else: # Fallback to keyring
            self.token = keyring.get_password(SERVICE_NAME, self.system_user)


    def init(self):
        if not self.token:
            if self.gh_available:
                try:
                    print("Using GitHub CLI to authenticate...")
                    subprocess.run([
                        "gh", "auth", "login",
                        "--scopes", "repo,read:org,gist,workflow,admin:org,delete_repo",
                    ], check=True)
                    self._load_token()
                except subprocess.CalledProcessError:
                    print("GitHub CLI authentication failed")

            else: # Fallback to keyring
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
        if response.lower() == "y":
            keyring.delete_password(SERVICE_NAME, self.system_user)
            print(f"Removed token for user '{self.system_user}'.")
