import pytest
import sys
from io import StringIO
from unittest.mock import patch, create_autospec

from ghot.ghot import main
from ghot.org_manager import OrgManager
from ghot.user import User

CSV = "id,username,repo\nid1,user1,repo1\nid2,user2,repo2\nid3,user3,repo3\n"


@pytest.mark.parametrize("ids, expected_ids", [
    pytest.param([], ["id1", "id2", "id3"], id="no_filter"),
    pytest.param(["--id", "id2"], ["id2"], id="single"),
    pytest.param(["--id", "id3", "--id", "id1"], ["id1", "id3"], id="multiple"),
])
@patch("ghot.ghot.init_org_manager", autospec=True)
def test_id_filter(mock_init_org_manager, ids, expected_ids, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "users.csv").write_text(CSV)
    monkeypatch.setattr(sys, "argv", ["ghot", "repo", "delete", "org", "users.csv", *ids])

    mock_org_manager = create_autospec(OrgManager)
    mock_init_org_manager.return_value = mock_org_manager

    main()

    users = mock_org_manager.repo_delete.call_args.args[1]
    assert [user.id for user in users] == expected_ids


@patch("ghot.ghot.init_org_manager", autospec=True)
def test_id_filter_not_found(mock_init_org_manager, monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "users.csv").write_text(CSV)
    monkeypatch.setattr(sys, "argv", ["ghot", "repo", "delete", "org", "users.csv", "--id", "id1", "--id", "nope"])

    mock_org_manager = create_autospec(OrgManager)
    mock_init_org_manager.return_value = mock_org_manager

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == "Id not found in users.csv: nope"
    mock_org_manager.repo_delete.assert_not_called()
