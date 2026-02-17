from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, OBJECTS_SUBDIR
from libcaf.plumbing import hash_file, open_content_for_reading
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_hash_file_without_write(temp_repo: Repository, temp_content: tuple[Path, str],
                                 capsys: CaptureFixture[str]) -> None:
    temp_file, _ = temp_content
    expected_hash = hash_file(temp_file)

    assert cli_commands.hash_file(path=temp_file,
                                  working_dir_path=temp_repo.working_dir,
                                  write=False) == 0
    assert f'Hash: {expected_hash}' in capsys.readouterr().out


def test_hash_file_with_write(temp_repo: Repository, temp_content: tuple[Path, str],
                              capsys: CaptureFixture[str]) -> None:
    temp_file, expected_content = temp_content
    expected_hash = hash_file(temp_file)

    assert cli_commands.hash_file(path=temp_file,
                                  working_dir_path=temp_repo.working_dir,
                                  write=True) == 0

    output = capsys.readouterr().out
    assert f'Hash: {expected_hash}' in output
    assert f'Saved file {temp_file} to CAF repository' in output

    with open_content_for_reading(temp_repo.working_dir / DEFAULT_REPO_DIR / OBJECTS_SUBDIR, expected_hash) as f:
        saved_content = f.read()

    assert saved_content == expected_content


def test_hash_file_does_not_exist(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    non_existent_file = temp_repo.working_dir / 'non_existent_file.txt'

    assert cli_commands.hash_file(path=non_existent_file,
                                  working_dir_path=temp_repo.working_dir,
                                  write=True) == -1
    assert f'File {non_existent_file} does not exist.' in capsys.readouterr().err


def test_hash_file_twice(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    temp_file = temp_repo.working_dir / 'test_file.txt'
    temp_file.write_text('This is a test file.')

    assert cli_commands.hash_file(path=temp_file,
                                  working_dir_path=temp_repo.working_dir,
                                  write=True) == 0
    assert cli_commands.hash_file(path=temp_file,
                                  working_dir_path=temp_repo.working_dir,
                                  write=True) == 0

    assert 'Hash: ' in capsys.readouterr().out


def test_hash_file_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    temp_file = temp_repo_dir / 'test_file.txt'
    temp_file.write_text('This is a test file.')

    assert cli_commands.hash_file(path=temp_file,
                                  working_dir_path=temp_repo_dir,
                                  write=True) == -1

    assert 'No repository found' in capsys.readouterr().err
