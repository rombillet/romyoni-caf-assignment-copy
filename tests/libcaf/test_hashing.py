from libcaf.constants import HASH_LENGTH
from libcaf.plumbing import hash_file, hash_object
from pytest import raises

from libcaf import Blob, Commit, Tree, TreeRecord, TreeRecordType


def test_hash_file_non_existent_file() -> None:
    with raises(RuntimeError):
        hash_file('test_hash_file_non_existent_file.txt')


def test_commit_hash() -> None:
    commit = Commit('1234567890abcdef', 'Author', 'Initial commit', 1234567890, '3234567890abcdef')
    commit_hash = hash_object(commit)

    assert commit_hash is not None
    assert len(commit_hash) == HASH_LENGTH


def test_commit_hash_parent_none() -> None:
    commit = Commit('1234567890abcdef', 'Author', 'Initial commit', 1234567890, None)
    commit_hash = hash_object(commit)

    assert commit_hash is not None
    assert len(commit_hash) == HASH_LENGTH


def test_tree_hash() -> None:
    record1 = TreeRecord(TreeRecordType.TREE, '1234567890abcdef', 'record1')
    record2 = TreeRecord(TreeRecordType.BLOB, 'abcdef1234567890', 'record2')

    tree = Tree({'record1': record1, 'record2': record2})
    tree_hash = hash_object(tree)

    assert tree_hash is not None
    assert len(tree_hash) == HASH_LENGTH


def test_same_blob_objects_get_same_hash() -> None:
    blob1 = Blob('1234567890abcdef')
    blob2 = Blob('1234567890abcdef')

    assert hash_object(blob1) == hash_object(blob2)


def test_same_commit_objects_get_same_hash() -> None:
    commit1 = Commit('1234567890abcdef', 'Author', 'Initial commit', 1234567890, 'aaabb12')
    commit2 = Commit('1234567890abcdef', 'Author', 'Initial commit', 1234567890, 'aaabb12')

    assert hash_object(commit1) == hash_object(commit2)


def test_same_commit_objects_get_same_hash_parent_none() -> None:
    commit1 = Commit('1234567890abcdef', 'Author', 'Initial commit', 1234567890, None)
    commit2 = Commit('1234567890abcdef', 'Author', 'Initial commit', 1234567890, None)

    assert hash_object(commit1) == hash_object(commit2)


def test_same_tree_objects_get_same_hash() -> None:
    record1 = TreeRecord(TreeRecordType.TREE, '1234567890abcdef', 'record1')
    record2 = TreeRecord(TreeRecordType.BLOB, 'abcdef1234567890', 'record2')

    tree1 = Tree({'record1': record1, 'record2': record2})
    tree2 = Tree({'record1': record1, 'record2': record2})

    assert hash_object(tree1) == hash_object(tree2)


def test_different_hashes_for_different_blobs() -> None:
    blob1 = Blob('1234567890abcdef')
    blob2 = Blob('abcdef1234567890')

    assert hash_object(blob1) != hash_object(blob2)


def test_different_hashes_for_different_trees() -> None:
    record1 = TreeRecord(TreeRecordType.TREE, '1234567890abcdef', 'record1')
    record2 = TreeRecord(TreeRecordType.BLOB, 'abcdef1234567890', 'record2')
    record3 = TreeRecord(TreeRecordType.TREE, 'fedcba0987654321', 'record3')

    tree1 = Tree({'record1': record1, 'record2': record2})
    tree2 = Tree({'record1': record1, 'record2': record3})

    assert hash_object(tree1) != hash_object(tree2)


def test_different_hashes_for_different_commits() -> None:
    commit1 = Commit('1234567890abcdef', 'Author1', 'Initial commit', 1234567890, None)
    commit2 = Commit('abcdef1234567890', 'Author2', 'Second commit', 1234567891, '2134567890abcdef')

    assert hash_object(commit1) != hash_object(commit2)


def test_different_hashes_for_different_parent_commits() -> None:
    commit1 = Commit('1234567890abcdef', 'Author', 'Commit message', 1234567890, 'parenthash1')
    commit2 = Commit('1234567890abcdef', 'Author', 'Commit message', 1234567890, 'parenthash2')

    hash1 = hash_object(commit1)
    hash2 = hash_object(commit2)

    assert hash1 != hash2, 'Hashes for commits with different parent hashes should not match'


def test_different_hashes_for_different_parent_commits_one_none() -> None:
    # Create two commits that differ only by the parent hash
    commit1 = Commit('1234567890abcdef', 'Author', 'Commit message', 1234567890, 'parenthash1')
    commit2 = Commit('1234567890abcdef', 'Author', 'Commit message', 1234567890, None)

    # Compute the hash for both commits
    hash1 = hash_object(commit1)
    hash2 = hash_object(commit2)

    # Verify the hashes are different
    assert hash1 != hash2, 'Hashes for commits with different parent hashes one none should not match'
