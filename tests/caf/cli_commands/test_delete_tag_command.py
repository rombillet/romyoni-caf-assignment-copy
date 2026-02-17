from pathlib import Path

from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def _create_tag(repo: Repository) -> str:
    temp_file = repo.working_dir / 'delete_tag.txt'
    temp_file.write_text('delete tag content')
    repo.save_file_content(temp_file)
    commit_ref = repo.commit_working_dir('Bob', 'tag commit')
    cli_commands.create_tag(working_dir_path=repo.working_dir, tag_name='v1', target=commit_ref)
    return commit_ref


def test_delete_tag_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    _create_tag(temp_repo)
    capsys.readouterr()

    assert cli_commands.delete_tag(working_dir_path=temp_repo.working_dir, tag_name='v1') == 0
    assert 'Tag "v1" deleted.' in capsys.readouterr().out


def test_delete_tag_missing_name(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(working_dir_path=temp_repo.working_dir) == -1
    assert 'Tag name is required' in capsys.readouterr().err


def test_delete_tag_unknown(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(working_dir_path=temp_repo.working_dir, tag_name='missing') == -1
    assert 'Repository error' in capsys.readouterr().err


def test_delete_tag_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.delete_tag(working_dir_path=temp_repo_dir, tag_name='v1') == -1
    assert 'No repository found' in capsys.readouterr().err
