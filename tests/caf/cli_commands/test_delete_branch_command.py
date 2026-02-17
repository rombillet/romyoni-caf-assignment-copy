from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, HEADS_DIR, REFS_DIR
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_delete_branch_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.add_branch(working_dir_path=temp_repo.working_dir, branch_name='feature') == 0
    assert cli_commands.delete_branch(working_dir_path=temp_repo.working_dir, branch_name='feature') == 0

    branch_path = temp_repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / HEADS_DIR / 'feature'
    assert not branch_path.exists()

    assert 'Branch "feature" deleted' in capsys.readouterr().out


def test_delete_branch_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_branch(working_dir_path=temp_repo_dir, branch_name='feature') == -1

    branch_path = temp_repo_dir / DEFAULT_REPO_DIR / REFS_DIR / HEADS_DIR / 'feature'
    assert not branch_path.exists()

    assert 'No repository found' in capsys.readouterr().err


def test_delete_branch_empty(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_branch(working_dir_path=temp_repo.working_dir, branch_name='') == -1
    assert 'Branch name is required' in capsys.readouterr().err


def test_delete_branch_does_not_exist(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_branch(working_dir_path=temp_repo.working_dir, branch_name='branch') == -1
    assert 'does not exist' in capsys.readouterr().err
