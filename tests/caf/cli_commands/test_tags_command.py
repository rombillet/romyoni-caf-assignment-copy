from pathlib import Path

from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def _create_tag(repo: Repository, name: str, content: str) -> None:
    tmp = repo.working_dir / f'{name}.txt'
    tmp.write_text(content)
    repo.save_file_content(tmp)
    commit_ref = repo.commit_working_dir('Lister', f'commit for {name}')
    repo.create_tag(name, commit_ref)


def test_tags_command_lists_tags(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    _create_tag(temp_repo, 'v1', 'content 1')
    _create_tag(temp_repo, 'v2', 'content 2')
    capsys.readouterr()

    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    output = capsys.readouterr().out
    assert 'Tags:' in output
    assert 'v1' in output
    assert 'v2' in output


def test_tags_command_no_tags(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.tags(working_dir_path=temp_repo.working_dir) == 0
    assert 'No tags found.' in capsys.readouterr().out


def test_tags_command_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.tags(working_dir_path=temp_repo_dir) == -1
    assert 'No repository found' in capsys.readouterr().err
