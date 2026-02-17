from pathlib import Path

from libcaf.constants import DEFAULT_BRANCH, DEFAULT_REPO_DIR, HEADS_DIR, HEAD_FILE, REFS_DIR
from libcaf.ref import SymRef, read_ref
from pytest import mark

from caf import cli_commands


@mark.parametrize('branch_name', [DEFAULT_BRANCH, 'develop'])
def test_init_repository(temp_repo_dir: Path, branch_name: str) -> None:
    assert cli_commands.init(working_dir_path=temp_repo_dir, default_branch=branch_name) == 0
    assert cli_commands.init(working_dir_path=temp_repo_dir, default_branch=branch_name) == -1

    repo_path = temp_repo_dir / DEFAULT_REPO_DIR
    assert repo_path.exists()

    main_branch = repo_path / REFS_DIR / HEADS_DIR / branch_name
    assert main_branch.read_text() == ''

    head_file = repo_path / HEAD_FILE
    assert read_ref(head_file) == SymRef(f'{HEADS_DIR}/{branch_name}')


def test_init_repository_str_working_dir(temp_repo_dir: Path) -> None:
    assert cli_commands.init(working_dir_path=str(temp_repo_dir)) == 0

    repo_path = temp_repo_dir / DEFAULT_REPO_DIR
    assert repo_path.exists()


def test_init_repository_str_repo_dir(temp_repo_dir: Path) -> None:
    assert cli_commands.init(working_dir_path=temp_repo_dir, repo_dir='.testcaf') == 0

    repo_path = temp_repo_dir / '.testcaf'
    assert repo_path.exists()
