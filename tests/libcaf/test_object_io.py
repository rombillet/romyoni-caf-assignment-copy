from pathlib import Path

from libcaf.plumbing import hash_object, load_commit, load_tree, save_commit, save_tree

from libcaf import Commit, Tree, TreeRecord, TreeRecordType


def test_save_load_commit(temp_repo_dir: Path) -> None:
    commit = Commit('tree_hash123', 'Author', 'Commit message', 1234567890, 'commithash123parent')
    commit_hash = hash_object(commit)

    save_commit(temp_repo_dir, commit)
    loaded_commit = load_commit(temp_repo_dir, commit_hash)

    assert loaded_commit.tree_hash == commit.tree_hash
    assert loaded_commit.author == commit.author
    assert loaded_commit.message == commit.message
    assert loaded_commit.timestamp == commit.timestamp
    assert loaded_commit.parent == commit.parent


def test_save_load_commit_without_parent(temp_repo_dir: Path) -> None:
    commit_none_parent = Commit('commithash456', 'Author', 'Commit message', 1234567890, None)
    commit_none_parent_hash = hash_object(commit_none_parent)

    save_commit(temp_repo_dir, commit_none_parent)
    loaded_commit_none_parent = load_commit(temp_repo_dir, commit_none_parent_hash)

    assert loaded_commit_none_parent.tree_hash == commit_none_parent.tree_hash
    assert loaded_commit_none_parent.author == commit_none_parent.author
    assert loaded_commit_none_parent.message == commit_none_parent.message
    assert loaded_commit_none_parent.timestamp == commit_none_parent.timestamp
    assert loaded_commit_none_parent.parent == commit_none_parent.parent


def test_save_load_tree(temp_repo_dir: Path) -> None:
    records = {
        'omer': TreeRecord(TreeRecordType.BLOB, 'omer123', 'omer'),
        'bar': TreeRecord(TreeRecordType.BLOB, 'bar123', 'bar'),
        'meshi': TreeRecord(TreeRecordType.BLOB, 'meshi123', 'meshi'),
    }
    tree = Tree(records)
    tree_hash = hash_object(tree)

    save_tree(temp_repo_dir, tree)
    loaded_tree = load_tree(temp_repo_dir, tree_hash)

    assert loaded_tree.records.keys() == records.keys()
    assert loaded_tree.records == records
