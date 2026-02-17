from pathlib import Path

from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def _create_commit(repo: Repository) -> str:
    sample = repo.working_dir / 'cli_tag.txt'
    sample.write_text('tag content')
    repo.save_file_content(sample)
    return repo.commit_working_dir('CLI Tester', 'prepare tag')


def test_create_tag_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    commit_ref = _create_commit(temp_repo)

    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name='v1', target=commit_ref) == 0
    output = capsys.readouterr().out
    assert 'Tag "v1" created' in output


def test_create_tag_missing_name(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    commit_ref = _create_commit(temp_repo)
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, target=commit_ref) == -1
    assert 'Tag name is required' in capsys.readouterr().err


def test_create_tag_missing_target(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name='v1') == -1
    assert 'Target commit hash is required' in capsys.readouterr().err


def test_create_tag_duplicate(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    commit_ref = _create_commit(temp_repo)
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name='v1', target=commit_ref) == 0
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name='v1', target=commit_ref) == -1
    assert 'already exists' in capsys.readouterr().err


def test_create_tag_invalid_target(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.create_tag(working_dir_path=temp_repo.working_dir, tag_name='bad', target='deadbeef') == -1
    assert 'Repository error' in capsys.readouterr().err


def test_create_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.create_tag(working_dir_path=temp_repo_dir, tag_name='v1', target='a' * 40) == -1
    assert 'No repository found' in capsys.readouterr().err
