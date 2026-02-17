from pathlib import Path

from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_delete_repo_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert (temp_repo.working_dir / '.caf').exists()
    assert cli_commands.delete_repo(working_dir_path=temp_repo.working_dir) == 0
    assert 'Deleted repository' in capsys.readouterr().out

    assert not (temp_repo.working_dir / '.caf').exists()
    assert cli_commands.delete_repo(working_dir_path=temp_repo.working_dir) == -1
    assert 'No repository found' in capsys.readouterr().err


def test_delete_repo_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert not (temp_repo_dir / '.caf').exists()
    assert cli_commands.delete_repo(working_dir_path=temp_repo_dir) == -1
    assert 'No repository found' in capsys.readouterr().err
