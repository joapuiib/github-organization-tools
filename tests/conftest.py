import pytest
from unittest.mock import MagicMock, patch

from ghot.user import User
from ghot.org_manager import OrgManager


@pytest.fixture
def fake_users():
    return [
        User("test.inexisting", "inexisting", None),
        User("test.existing", "existing", "existing-repo"),
        User("test.invited", "invited", None),
        User("test.user1", "user1", "user1-repo", "Repository for user1"),
        User("test.user2", "user2", "user2-repo"),
        User("test.user3", "user3", None),
        User("test.user4", None, None),     # Invalid user
        User(None, None, None),             # Invalid user
    ]


@pytest.fixture
def manager():
    gh_client_mock = MagicMock()
    org_mock = MagicMock(login="org")
    gh_client_mock.get_user.side_effect = lambda x: MagicMock(id=x, login=x) if x != "not_exists" else None
    gh_client_mock.get_organization.return_value = org_mock

    def get_repo_side_effect(repo_id):
        if repo_id == "org/not_exists":
            return None
        mock_repo = MagicMock(repo_id=repo_id)
        mock_repo.get_collaborators.return_value = [MagicMock(login="repo_collaborator")]
        mock_repo.get_pending_invitations.return_value = [MagicMock(invitee=MagicMock(login="repo_invited"))]
        mock_repo.clone_url = f"HTTPS_URL/{repo_id}"
        mock_repo.ssh_url = f"SSH_URL/{repo_id}"

        create_issue_mock = MagicMock(name="create_issue()")
        create_issue_mock.number = "issue_number"
        mock_repo.create_issue.return_value = create_issue_mock

        return mock_repo
    gh_client_mock.get_repo.side_effect = get_repo_side_effect

    org_mock.get_members.return_value = [
        MagicMock(login="member"),
        MagicMock(login="member_cancelled"),
        MagicMock(login="repo_collaborator"),
        MagicMock(login="repo_invited"),
    ]
    org_mock.invitations.return_value = [
        MagicMock(login="org_invited"),
        MagicMock(login="org_invited_cancelled"),
    ]

    manager = OrgManager(gh_client_mock)
    manager._confirm_prompt = lambda x: False if "cancelled" in x else True
    return manager
