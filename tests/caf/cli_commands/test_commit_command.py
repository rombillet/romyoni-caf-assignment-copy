from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, HEAD_FILE
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_commit_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    author, message = 'John Doe', 'Initial commit'

    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Initial commit content')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author=author, message=message) == 0

    output = capsys.readouterr().out
    assert 'Commit created successfully:' in output
    assert f'Author: {author}' in output
    assert f'Message: {message}' in output
    assert 'Hash: ' in output


def test_commit_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    temp_file = temp_repo_dir / 'test_file.txt'
    temp_file.write_text('Content of test_file')

    assert cli_commands.commit(working_dir_path=temp_repo_dir,
                               author='Test Author',
                               message='Test commit message') == -1

    assert 'No repository found' in capsys.readouterr().err


def test_commit_repo_error(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    (temp_repo.working_dir / DEFAULT_REPO_DIR / HEAD_FILE).unlink()
    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author='Test Author',
                               message='Test commit message') == -1

    assert 'Repository error' in capsys.readouterr().err


def test_commit_missing_author(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Content of test_file')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author=None, message='Test commit message') == -1

    assert 'Author' in capsys.readouterr().err


def test_commit_missing_message(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('Content of test_file')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author='Test Author', message=None) == -1

    assert 'Commit message' in capsys.readouterr().err
