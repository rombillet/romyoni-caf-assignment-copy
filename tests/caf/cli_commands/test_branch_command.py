from pathlib import Path

from libcaf.constants import (DEFAULT_BRANCH, DEFAULT_REPO_DIR, HEADS_DIR, HEAD_FILE, REFS_DIR)
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_branch_command(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    branches = ['branch_1', 'branch_2', 'branch_3', 'branch_4', 'branch_5']

    for branch in branches:
        cli_commands.add_branch(working_dir_path=temp_repo.working_dir, branch_name=branch)

    capsys.readouterr()

    assert cli_commands.branch(working_dir_path=temp_repo.working_dir) == 0

    branch_names: list[str] = []
    lines = capsys.readouterr().out.splitlines()
    for index, line in enumerate(lines):
        if index != 0:
            branch_names.append(line.strip().split()[-1])

    expected_branches = {'main'} | set(branches)
    assert len(branch_names) == len(expected_branches)
    assert set(branch_names) == expected_branches


def test_branch_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.branch(working_dir_path=temp_repo_dir) == -1

    assert 'No repository found' in capsys.readouterr().err


def test_branch_no_branches(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    (temp_repo.working_dir / DEFAULT_REPO_DIR / REFS_DIR / HEADS_DIR / DEFAULT_BRANCH).unlink()
    assert cli_commands.branch(working_dir_path=temp_repo.working_dir) == 0

    assert 'No branches found' in capsys.readouterr().out


def test_branch_repo_error(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    (temp_repo.working_dir / DEFAULT_REPO_DIR / HEAD_FILE).unlink()
    assert cli_commands.branch(working_dir_path=temp_repo.working_dir) == -1

    assert 'Repository error' in capsys.readouterr().err


def test_branch_shows_current_branch_with_asterisk(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    cli_commands.add_branch(working_dir_path=temp_repo.working_dir, branch_name='feature')
    cli_commands.add_branch(working_dir_path=temp_repo.working_dir, branch_name='develop')

    capsys.readouterr()

    assert cli_commands.branch(working_dir_path=temp_repo.working_dir) == 0

    output = capsys.readouterr().out
    lines = output.splitlines()

    current_branch_line = None
    other_branch_lines: list[str] = []
    for line in lines[1:]:  # Skip the "Branches:" header
        if line.strip().startswith('* '):
            current_branch_line = line.strip()

    # The current branch should be marked with asterisk (should be 'main' by default)
    assert current_branch_line is not None, 'No branch marked with asterisk found'
    assert current_branch_line == f'* {DEFAULT_BRANCH}', f"Expected '* {DEFAULT_BRANCH}', got '{current_branch_line}'"

    # Other branches should not have asterisk
    for line in other_branch_lines:
        assert not line.startswith('* '), f"Branch '{line}' should not have asterisk"
