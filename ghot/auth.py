import getpass
import keyring
from github import Github, Auth

SERVICE_NAME = "github_pat"

class AuthManager:
    def __init__(self):
        self.system_user = getpass.getuser()
        self._load_token()


    def _load_token(self):
        self.token = keyring.get_password(SERVICE_NAME, self.system_user)


    def init(self):
        if not self.token:
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
