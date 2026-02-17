from collections.abc import Sequence

from libcaf.repository import (AddedDiff, Diff, ModifiedDiff, MovedFromDiff, MovedToDiff, RemovedDiff, Repository)


def split_diffs_by_type(diffs: Sequence[Diff]) -> \
        tuple[list[AddedDiff],
        list[ModifiedDiff],
        list[MovedToDiff],
        list[MovedFromDiff],
        list[RemovedDiff]]:
    added = [d for d in diffs if isinstance(d, AddedDiff)]
    moved_to = [d for d in diffs if isinstance(d, MovedToDiff)]
    moved_from = [d for d in diffs if isinstance(d, MovedFromDiff)]
    removed = [d for d in diffs if isinstance(d, RemovedDiff)]
    modified = [d for d in diffs if isinstance(d, ModifiedDiff)]

    return added, modified, moved_to, moved_from, removed


def test_diff_head(temp_repo: Repository) -> None:
    file_path = temp_repo.working_dir / 'file.txt'
    file_path.write_text('Same content')

    temp_repo.commit_working_dir('Tester', 'Initial commit')
    diff_result = temp_repo.diff_commits()

    assert len(diff_result) == 0


def test_diff_identical_commits(temp_repo: Repository) -> None:
    file_path = temp_repo.working_dir / 'file.txt'
    file_path.write_text('Same content')

    commit_hash = temp_repo.commit_working_dir('Tester', 'Initial commit')
    diff_result = temp_repo.diff_commits(commit_hash, 'HEAD')

    assert len(diff_result) == 0


def test_diff_added_file(temp_repo: Repository) -> None:
    file1 = temp_repo.working_dir / 'file1.txt'
    file1.write_text('Content 1')
    commit1_hash = temp_repo.commit_working_dir('Tester', 'Initial commit')

    file2 = temp_repo.working_dir / 'file2.txt'
    file2.write_text('Content 2')
    temp_repo.commit_working_dir('Tester', 'Added file2')

    diff_result = temp_repo.diff_commits(commit1_hash)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 1
    assert added[0].record.name == 'file2.txt'

    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0
    assert len(modified) == 0


def test_diff_removed_file(temp_repo: Repository) -> None:
    file1 = temp_repo.working_dir / 'file.txt'
    file1.write_text('Content')
    commit1_hash = temp_repo.commit_working_dir('Tester', 'File created')

    file1.unlink()  # Delete the file.
    temp_repo.commit_working_dir('Tester', 'File deleted')

    diff_result = temp_repo.diff_commits(commit1_hash)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(modified) == 0

    assert len(removed) == 1
    assert removed[0].record.name == 'file.txt'


def test_diff_modified_file(temp_repo: Repository) -> None:
    file1 = temp_repo.working_dir / 'file.txt'
    file1.write_text('Old content')
    commit1 = temp_repo.commit_working_dir('Tester', 'Original commit')

    file1.write_text('New content')
    commit2 = temp_repo.commit_working_dir('Tester', 'Modified file')

    diff_result = temp_repo.diff_commits(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 1
    assert modified[0].record.name == 'file.txt'


def test_diff_nested_directory(temp_repo: Repository) -> None:
    subdir = temp_repo.working_dir / 'subdir'
    subdir.mkdir()
    nested_file = subdir / 'file.txt'
    nested_file.write_text('Initial')
    commit1 = temp_repo.commit_working_dir('Tester', 'Commit with subdir')

    nested_file.write_text('Modified')
    commit2 = temp_repo.commit_working_dir('Tester', 'Modified nested file')

    diff_result = temp_repo.diff_commits(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 1
    assert modified[0].record.name == 'subdir'
    assert len(modified[0].children) == 1
    assert modified[0].children[0].record.name == 'file.txt'


def test_diff_nested_trees(temp_repo: Repository) -> None:
    dir1 = temp_repo.working_dir / 'dir1'
    dir1.mkdir()
    file_a = dir1 / 'file_a.txt'
    file_a.write_text('A1')

    dir2 = temp_repo.working_dir / 'dir2'
    dir2.mkdir()
    file_b = dir2 / 'file_b.txt'
    file_b.write_text('B1')

    commit1 = temp_repo.commit_working_dir('Tester', 'Initial nested commit')

    file_a.write_text('A2')
    file_b.unlink()
    file_c = dir2 / 'file_c.txt'
    file_c.write_text('C1')

    commit2 = temp_repo.commit_working_dir('Tester', 'Updated nested commit')

    diff_result = temp_repo.diff_commits(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 2

    assert modified[0].record.name == 'dir1'
    assert len(modified[0].children) == 1
    assert modified[0].children[0].record.name == 'file_a.txt'
    assert isinstance(modified[0].children[0], ModifiedDiff)

    assert modified[1].record.name == 'dir2'
    assert len(modified[1].children) == 2
    assert modified[1].children[0].record.name == 'file_b.txt'
    assert isinstance(modified[1].children[0], RemovedDiff)
    assert modified[1].children[1].record.name == 'file_c.txt'
    assert isinstance(modified[1].children[1], AddedDiff)


def test_diff_moved_file_added_first(temp_repo: Repository) -> None:
    dir1 = temp_repo.working_dir / 'dir1'
    dir1.mkdir()
    file_a = dir1 / 'file_a.txt'
    file_a.write_text('A1')

    dir2 = temp_repo.working_dir / 'dir2'
    dir2.mkdir()
    file_b = dir2 / 'file_b.txt'
    file_b.write_text('B1')

    commit1 = temp_repo.commit_working_dir('Tester', 'Initial nested commit')

    file_a.rename(dir2 / 'file_c.txt')

    commit2 = temp_repo.commit_working_dir('Tester', 'Updated nested commit')

    diff_result = temp_repo.diff_commits(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 2

    assert modified[0].record.name == 'dir1'
    assert len(modified[0].children) == 1

    modified_child = modified[0].children[0]
    assert isinstance(modified_child, MovedToDiff)
    assert modified_child.record.name == 'file_a.txt'

    assert isinstance(modified_child.moved_to, MovedFromDiff)
    assert modified_child.moved_to.parent is not None
    assert modified_child.moved_to.parent.record.name == 'dir2'
    assert len(modified_child.moved_to.parent.children) == 1
    assert modified_child.moved_to.record.name == 'file_c.txt'

    assert modified[1].record.name == 'dir2'
    assert len(modified[1].children) == 1

    modified_child = modified[1].children[0]
    assert isinstance(modified_child, MovedFromDiff)
    assert modified_child.record.name == 'file_c.txt'

    assert isinstance(modified_child.moved_from, MovedToDiff)
    assert modified_child.moved_from.parent is not None
    assert modified_child.moved_from.parent.record.name == 'dir1'
    assert len(modified_child.moved_from.parent.children) == 1
    assert modified_child.moved_from.record.name == 'file_a.txt'


def test_diff_moved_file_removed_first(temp_repo: Repository) -> None:
    dir1 = temp_repo.working_dir / 'dir1'
    dir1.mkdir()
    file_a = dir1 / 'file_a.txt'
    file_a.write_text('A1')

    dir2 = temp_repo.working_dir / 'dir2'
    dir2.mkdir()
    file_b = dir2 / 'file_b.txt'
    file_b.write_text('B1')

    commit1 = temp_repo.commit_working_dir('Tester', 'Initial nested commit')

    file_b.rename(dir1 / 'file_c.txt')

    commit2 = temp_repo.commit_working_dir('Tester', 'Updated nested commit')

    diff_result = temp_repo.diff_commits(commit1, commit2)
    added, modified, moved_to, moved_from, removed = \
        split_diffs_by_type(diff_result)

    assert len(added) == 0
    assert len(moved_to) == 0
    assert len(moved_from) == 0
    assert len(removed) == 0

    assert len(modified) == 2

    assert modified[0].record.name == 'dir1'
    assert len(modified[0].children) == 1

    modified_child = modified[0].children[0]
    assert isinstance(modified_child, MovedFromDiff)
    assert modified_child.record.name == 'file_c.txt'

    assert isinstance(modified_child.moved_from, MovedToDiff)
    assert modified_child.moved_from.parent is not None
    assert modified_child.moved_from.parent.record.name == 'dir2'
    assert len(modified_child.moved_from.parent.children) == 1
    assert modified_child.moved_from.record.name == 'file_b.txt'

    assert modified[1].record.name == 'dir2'
    assert len(modified[1].children) == 1

    modified_child = modified[1].children[0]
    assert isinstance(modified_child, MovedToDiff)
    assert modified_child.record.name == 'file_b.txt'

    assert isinstance(modified_child.moved_to, MovedFromDiff)
    assert modified_child.moved_to.parent is not None
    assert len(modified_child.moved_to.parent.children) == 1
    assert modified_child.moved_to.parent.record.name == 'dir1'
    assert modified_child.moved_to.record.name == 'file_c.txt'
