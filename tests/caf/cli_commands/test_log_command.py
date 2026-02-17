from collections.abc import Callable
from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, HEAD_FILE
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_log_command(temp_repo: Repository, parse_commit_hash: Callable[[], str], capsys: CaptureFixture[str]) -> None:
    working_dir = temp_repo.working_dir
    temp_file = working_dir / 'log_test.txt'
    temp_file.write_text('First commit content')

    assert cli_commands.commit(working_dir_path=working_dir,
                               author='Log Tester', message='First commit') == 0
    commit_hash1 = parse_commit_hash()

    temp_file.write_text('Second commit content')
    assert cli_commands.commit(working_dir_path=working_dir,
                               author='Log Tester', message='Second commit') == 0
    commit_hash2 = parse_commit_hash()

    assert cli_commands.log(working_dir_path=working_dir) == 0

    output: str = capsys.readouterr().out
    assert commit_hash1 in output
    assert commit_hash2 in output
    assert 'Log Tester' in output
    assert 'First commit' in output
    assert 'Second commit' in output


def test_log_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.log(working_dir_path=temp_repo_dir) == -1
    assert 'No repository found' in capsys.readouterr().err


def test_log_repo_error(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    working_dir = temp_repo.working_dir
    (working_dir / DEFAULT_REPO_DIR / HEAD_FILE).unlink()
    assert cli_commands.log(working_dir_path=working_dir) == -1

    assert 'Repository error' in capsys.readouterr().err


def test_log_no_commits(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.log(working_dir_path=temp_repo.working_dir) == 0
    assert 'No commits in the repository' in capsys.readouterr().out
