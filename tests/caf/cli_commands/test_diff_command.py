from collections.abc import Callable
from pathlib import Path

from libcaf.constants import DEFAULT_REPO_DIR, HEAD_FILE
from libcaf.repository import Repository
from pytest import CaptureFixture

from caf import cli_commands


def test_diff_added_file(temp_repo: Repository, parse_commit_hash: Callable[[], str],
                         capsys: CaptureFixture[str]) -> None:
    (temp_repo.working_dir / 'file1.txt').write_text('Content of file1')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Initial commit') == 0
    commit_hash1 = parse_commit_hash()

    file2 = temp_repo.working_dir / 'file2.txt'
    file2.write_text('Content of file2')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Added file2') == 0
    commit_hash2 = parse_commit_hash()

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir, commit1=commit_hash1, commit2=commit_hash2) == 0
    assert 'Added: file2.txt' in capsys.readouterr().out


def test_diff_modified_file(temp_repo: Repository, parse_commit_hash: Callable[[], str],
                            capsys: CaptureFixture[str]) -> None:
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Original content')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Initial commit') == 0
    commit_hash1 = parse_commit_hash()

    file1.write_text('Modified content')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Modified file1') == 0
    commit_hash2 = parse_commit_hash()

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir, commit1=commit_hash1, commit2=commit_hash2) == 0
    assert 'Modified: file1.txt' in capsys.readouterr().out


def test_diff_removed_file(temp_repo: Repository, parse_commit_hash: Callable[[], str],
                           capsys: CaptureFixture[str]) -> None:
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Content of file1')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Initial commit') == 0
    commit_hash1 = parse_commit_hash()

    file1.unlink()

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Removed file1') == 0
    commit_hash2 = parse_commit_hash()

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir, commit1=commit_hash1, commit2=commit_hash2) == 0
    assert 'Removed: file1.txt' in capsys.readouterr().out


def test_diff_moved_file(temp_repo: Repository, parse_commit_hash: Callable[[], str],
                         capsys: CaptureFixture[str]) -> None:
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Content of file1')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Initial commit') == 0
    commit_hash1 = parse_commit_hash()

    moved_file = temp_repo.working_dir / 'moved_file.txt'
    file1.rename(moved_file)

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Moved file1') == 0
    commit_hash2 = parse_commit_hash()

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir, commit1=commit_hash1, commit2=commit_hash2) == 0
    assert 'Moved: file1.txt -> moved_file.txt' in capsys.readouterr().out


def test_diff_command_compound(temp_repo: Repository, parse_commit_hash: Callable[[], str],
                               capsys: CaptureFixture[str]) -> None:
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Version 1')
    file_to_remove = temp_repo.working_dir / 'file_to_remove.txt'
    file_to_remove.write_text('This file will be removed')
    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author='Diff Tester',
                               message='First commit') == 0
    commit_hash1 = parse_commit_hash()

    file1.write_text('Version 2')
    file2 = temp_repo.working_dir / 'file2.txt'
    file2.write_text('New file')
    # Add a file that will be moved in the next commit
    file_to_move = temp_repo.working_dir / 'file_to_move.txt'
    file_to_move.write_text('Content that will be moved')
    # Remove the file that was added in the first commit
    file_to_remove.unlink()
    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author='Diff Tester', message='Second commit') == 0
    commit_hash2 = parse_commit_hash()

    # Create a third commit that moves the file
    moved_file = temp_repo.working_dir / 'moved_file.txt'
    file_to_move.rename(moved_file)
    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author='Diff Tester', message='Third commit with moved file') == 0
    commit_hash3 = parse_commit_hash()

    # Test diff between first and second commit (added/modified/removed files)
    assert cli_commands.diff(working_dir_path=temp_repo.working_dir,
                             commit1=commit_hash1,
                             commit2=commit_hash2) == 0

    output = capsys.readouterr().out
    assert 'Diff:' in output
    assert 'Added: file2.txt' in output
    assert 'Modified: file1.txt' in output
    assert 'Added: file_to_move.txt' in output
    assert 'Removed: file_to_remove.txt' in output

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir,
                             commit1=commit_hash2,
                             commit2=commit_hash3) == 0

    output = capsys.readouterr().out
    assert 'Diff:' in output
    assert 'Moved: file_to_move.txt -> moved_file.txt' in output


def test_diff_no_repo(temp_repo_dir: Path, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.diff(working_dir_path=temp_repo_dir,
                             commit1='abc123', commit2='def456') == -1

    assert 'No repository found' in capsys.readouterr().err


def test_diff_repo_error(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    (temp_repo.working_dir / DEFAULT_REPO_DIR / HEAD_FILE).unlink()
    assert cli_commands.diff(working_dir_path=temp_repo.working_dir,
                             commit1='abc123', commit2='def456') == -1

    assert 'Repository error' in capsys.readouterr().err


def test_diff_missing_parameters(temp_repo: Repository, capsys: CaptureFixture[str]) -> None:
    assert cli_commands.diff(working_dir_path=temp_repo.working_dir,
                             commit1=None, commit2='def456') == -1
    assert 'Both commit1 and commit2' in capsys.readouterr().err

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir,
                             commit1='abc123', commit2=None) == -1
    assert 'Both commit1 and commit2' in capsys.readouterr().err

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir,
                             commit1=None, commit2=None) == -1
    assert 'Both commit1 and commit2' in capsys.readouterr().err


def test_diff_no_changes(temp_repo: Repository, parse_commit_hash: Callable[[], str],
                         capsys: CaptureFixture[str]) -> None:
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Content')
    assert cli_commands.commit(working_dir_path=temp_repo.working_dir, author='Test', message='Commit') == 0
    commit_hash = parse_commit_hash()

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir,
                             commit1=commit_hash, commit2=commit_hash) == 0
    assert 'No changes detected between commits' in capsys.readouterr().out


def test_diff_nested_children_indentation(temp_repo: Repository, parse_commit_hash: Callable[[], str],
                                          capsys: CaptureFixture[str]) -> None:
    subdir = temp_repo.working_dir / 'subdir'
    subdir.mkdir()

    file1 = subdir / 'nested_file1.txt'
    file1.write_text('Content of nested file 1')
    file2 = subdir / 'nested_file2.txt'
    file2.write_text('Content of nested file 2')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author='Test Author',
                               message='Initial commit with nested files') == 0
    commit_hash1 = parse_commit_hash()

    file1.write_text('Modified content of nested file 1')
    file3 = subdir / 'nested_file3.txt'
    file3.write_text('Content of new nested file 3')

    assert cli_commands.commit(working_dir_path=temp_repo.working_dir,
                               author='Test Author',
                               message='Modified and added nested files') == 0
    commit_hash2 = parse_commit_hash()

    assert cli_commands.diff(working_dir_path=temp_repo.working_dir,
                             commit1=commit_hash1,
                             commit2=commit_hash2) == 0

    # Verify that nested children are displayed with proper indentation
    # The subdir should be modified, and its children should be indented
    output = capsys.readouterr().out
    lines = output.split('\n')
    found_directory_diff = False
    found_nested_indentation = False
    for i, line in enumerate(lines):
        if 'Modified: subdir' in line:
            found_directory_diff = True
            # Check subsequent lines for nested children with indentation
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j].startswith(' ' * 3):  # 3 spaces indentation (indent + 3)
                    found_nested_indentation = True
                    break

    assert found_directory_diff, 'Directory modification should be detected'
    assert found_nested_indentation, 'Nested children should be indented by 3 spaces'
