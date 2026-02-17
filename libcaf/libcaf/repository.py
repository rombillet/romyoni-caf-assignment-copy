"""libcaf repository management."""

import shutil
from collections import deque
from collections.abc import Callable, Generator, Sequence
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Concatenate

from . import Blob, Commit, Tree, TreeRecord, TreeRecordType
from .constants import (DEFAULT_BRANCH, DEFAULT_REPO_DIR, HASH_CHARSET, HASH_LENGTH, HEADS_DIR, HEAD_FILE,
                        OBJECTS_SUBDIR, REFS_DIR, TAGS_DIR)
from .merge import MergeError, MergeResult, find_common_ancestor_core, merge_commits_core
from .plumbing import hash_object, load_commit, load_tree, save_commit, save_file_content, save_tree
from .ref import HashRef, Ref, RefError, SymRef, read_ref, write_ref


class RepositoryError(Exception):
    """Exception raised for repository-related errors."""


class RepositoryNotFoundError(RepositoryError):
    """Exception raised when a repository is not found."""


@dataclass
class Diff:
    """A class representing a difference between two tree records."""

    record: TreeRecord
    parent: 'Diff | None'
    children: list['Diff']


@dataclass
class AddedDiff(Diff):
    """An added tree record diff as part of a commit."""


@dataclass
class RemovedDiff(Diff):
    """A removed tree record diff as part of a commit."""


@dataclass
class ModifiedDiff(Diff):
    """A modified tree record diff as part of a commit."""


@dataclass
class MovedToDiff(Diff):
    """A tree record diff that has been moved elsewhere as part of a commit."""

    moved_to: 'MovedFromDiff | None'


@dataclass
class MovedFromDiff(Diff):
    """A tree record diff that has been moved from elsewhere as part of a commit."""

    moved_from: MovedToDiff | None


@dataclass
class LogEntry:
    """A class representing a log entry for a branch or commit history."""

    commit_ref: HashRef
    commit: Commit


@dataclass
class Tag:
    """Represents an immutable label that points to a commit."""

    name: str
    target: HashRef


class Repository:
    """Represents a libcaf repository.

    This class provides methods to initialize a repository, manage branches,
    commit changes, and perform various operations on the repository."""

    def __init__(self, working_dir: Path | str, repo_dir: Path | str | None = None) -> None:
        """Initialize a Repository instance. The repository is not created on disk until `init()` is called.

        :param working_dir: The working directory where the repository will be located.
        :param repo_dir: The name of the repository directory within the working directory. Defaults to '.caf'."""
        self.working_dir = Path(working_dir)

        if repo_dir is None:
            self.repo_dir = Path(DEFAULT_REPO_DIR)
        else:
            self.repo_dir = Path(repo_dir)

    def init(self, default_branch: str = DEFAULT_BRANCH) -> None:
        """Initialize a new CAF repository in the working directory.

        :param default_branch: The name of the default branch to create. Defaults to 'main'.
        :raises RepositoryError: If the repository already exists or if the working directory is invalid."""
        self.repo_path().mkdir(parents=True)
        self.objects_dir().mkdir()

        heads_dir = self.heads_dir()
        heads_dir.mkdir(parents=True)
        self.tags_dir().mkdir(parents=True)

        self.add_branch(default_branch)

        write_ref(self.head_file(), branch_ref(default_branch))

    def exists(self) -> bool:
        """Check if the repository exists in the working directory.

        :return: True if the repository exists, False otherwise."""
        return self.repo_path().exists()

    def repo_path(self) -> Path:
        """Get the path to the repository directory.

        :return: The path to the repository directory."""
        return self.working_dir / self.repo_dir

    def objects_dir(self) -> Path:
        """Get the path to the objects directory within the repository.

        :return: The path to the objects directory."""
        return self.repo_path() / OBJECTS_SUBDIR

    def refs_dir(self) -> Path:
        """Get the path to the refs directory within the repository.

        :return: The path to the refs directory."""
        return self.repo_path() / REFS_DIR

    def heads_dir(self) -> Path:
        """Get the path to the heads directory within the repository.

        :return: The path to the heads directory."""
        return self.refs_dir() / HEADS_DIR

    def tags_dir(self) -> Path:
        """Get the path to the tags directory within the repository."""
        return self.refs_dir() / TAGS_DIR

    @staticmethod
    def requires_repo[**P, R](func: Callable[Concatenate['Repository', P], R]) -> \
            Callable[Concatenate['Repository', P], R]:
        """Decorate a Repository method to ensure that the repository exists before executing the method.

        :param func: The method to decorate.
        :return: A wrapper function that checks for the repository's existence."""

        @wraps(func)
        def _verify_repo(self: 'Repository', *args: P.args, **kwargs: P.kwargs) -> R:
            if not self.exists():
                msg = f'Repository not initialized at {self.repo_path()}'
                raise RepositoryNotFoundError(msg)

            return func(self, *args, **kwargs)

        return _verify_repo

    @requires_repo
    def head_ref(self) -> Ref | None:
        """Get the current HEAD reference of the repository.

        :return: The current HEAD reference, which can be a HashRef or SymRef.
        :raises RepositoryError: If the HEAD ref file does not exist.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        head_file = self.head_file()
        if not head_file.exists():
            msg = 'HEAD ref file does not exist'
            raise RepositoryError(msg)

        return read_ref(head_file)

    @requires_repo
    def head_commit(self) -> HashRef | None:
        """Return a ref to the current commit reference of the HEAD.

        :return: The current commit reference, or None if HEAD is not a commit.
        :raises RepositoryError: If the HEAD ref file does not exist.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        # If HEAD is a symbolic reference, resolve it to a hash
        resolved_ref = self.resolve_ref(self.head_ref())
        if resolved_ref:
            return resolved_ref
        return None

    @requires_repo
    def refs(self) -> list[SymRef]:
        """Get a list of all symbolic references in the repository.

        :return: A list of SymRef objects representing the symbolic references.
        :raises RepositoryError: If the refs directory does not exist or is not a directory.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        refs_dir = self.refs_dir()
        if not refs_dir.exists() or not refs_dir.is_dir():
            msg = f'Refs directory does not exist or is not a directory: {refs_dir}'
            raise RepositoryError(msg)

        refs: list[SymRef] = [SymRef(ref_file.name) for ref_file in refs_dir.rglob('*')
                              if ref_file.is_file()]

        return refs

    @requires_repo
    def resolve_ref(self, ref: Ref | str | None) -> HashRef | None:
        """Resolve a reference to a HashRef, following symbolic references if necessary.

        :param ref: The reference to resolve. This can be a HashRef, SymRef, or a string.
        :return: The resolved HashRef or None if the reference does not exist.
        :raises RefError: If the reference is invalid or cannot be resolved.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        match ref:
            case HashRef():
                return ref
            case SymRef(ref):
                if ref.upper() == 'HEAD':
                    return self.resolve_ref(self.head_ref())

                ref = read_ref(self.refs_dir() / ref)
                return self.resolve_ref(ref)
            case str():
                # Try to figure out what kind of ref it is by looking at the list of refs
                # in the refs directory
                if ref.upper() == 'HEAD' or ref in self.refs():
                    return self.resolve_ref(SymRef(ref))
                if len(ref) == HASH_LENGTH and all(c in HASH_CHARSET for c in ref):
                    return HashRef(ref)

                msg = f'Invalid reference: {ref}'
                raise RefError(msg)
            case None:
                return None
            case _:
                msg = f'Invalid reference type: {type(ref)}'
                raise RefError(msg)

    @requires_repo
    def update_ref(self, ref_name: str, new_ref: Ref) -> None:
        """Update a symbolic reference in the repository.

        :param ref_name: The name of the symbolic reference to update.
        :param new_ref: The new reference value to set.
        :raises RepositoryError: If the reference does not exist.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        ref_path = self.refs_dir() / ref_name

        if not ref_path.exists():
            msg = f'Reference "{ref_name}" does not exist.'
            raise RepositoryError(msg)

        write_ref(ref_path, new_ref)

    @requires_repo
    def delete_repo(self) -> None:
        """Delete the entire repository, including all objects and refs.

        :raises RepositoryNotFoundError: If the repository does not exist."""
        shutil.rmtree(self.repo_path())

    @requires_repo
    def save_file_content(self, file: Path) -> Blob:
        """Save the content of a file to the repository.

        :param file: The path to the file to save.
        :return: A Blob object representing the saved file content.
        :raises ValueError: If the file does not exist.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        return save_file_content(self.objects_dir(), file)

    @requires_repo
    def add_branch(self, branch: str) -> None:
        """Add a new branch to the repository, initialized to be an empty reference.

        :param branch: The name of the branch to add.
        :raises ValueError: If the branch name is empty.
        :raises RepositoryError: If the branch already exists.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        if not branch:
            msg = 'Branch name is required'
            raise ValueError(msg)
        if self.branch_exists(SymRef(branch)):
            msg = f'Branch "{branch}" already exists'
            raise RepositoryError(msg)

        (self.heads_dir() / branch).touch()

    @requires_repo
    def create_tag(self, tag_name: str, target: Ref | str) -> Tag:
        """Create a new tag that points to the given target commit.

        :param tag_name: The name of the tag to create.
        :param target: The reference (commit hash, branch, or tag) the new tag should point to.
        :return: The created Tag.
        :raises ValueError: If the tag name is empty.
        :raises RepositoryError: If the tag already exists or the target cannot be resolved.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        if not tag_name:
            msg = 'Tag name is required'
            raise ValueError(msg)

        tag_path = self.tags_dir() / tag_name
        if tag_path.exists():
            msg = f'Tag "{tag_name}" already exists'
            raise RepositoryError(msg)

        try:
            resolved_target = self.resolve_ref(target)
        except RefError as exc:
            msg = f'Cannot resolve target \"{target}\" for tag \"{tag_name}\"'
            raise RepositoryError(msg) from exc
        if resolved_target is None:
            msg = f'Cannot resolve target "{target}" for tag "{tag_name}"'
            raise RepositoryError(msg)

        try:
            load_commit(self.objects_dir(), resolved_target)
        except Exception as exc:
            msg = f'Cannot create tag \"{tag_name}\" because commit {resolved_target} does not exist'
            raise RepositoryError(msg) from exc

        tag_path.parent.mkdir(parents=True, exist_ok=True)
        write_ref(tag_path, resolved_target)

        return Tag(tag_name, resolved_target)

    @requires_repo
    def delete_tag(self, tag_name: str) -> None:
        """Delete a tag from the repository."""
        if not tag_name:
            msg = 'Tag name is required'
            raise ValueError(msg)

        tag_path = self.tags_dir() / tag_name
        if not tag_path.exists():
            msg = f'Tag "{tag_name}" does not exist.'
            raise RepositoryError(msg)

        tag_path.unlink()

    @requires_repo
    def list_tags(self) -> list[Tag]:
        """Return all tags sorted by name."""
        tags_dir = self.tags_dir()
        if not tags_dir.exists():
            return []

        tags: list[Tag] = []
        for tag_file in tags_dir.iterdir():
            if not tag_file.is_file():
                continue

            tag_ref_value = read_ref(tag_file)
            if not isinstance(tag_ref_value, HashRef):
                msg = f'Invalid tag reference stored in {tag_file}'
                raise RepositoryError(msg)

            tags.append(Tag(tag_file.name, tag_ref_value))

        tags.sort(key=lambda tag: tag.name)
        return tags

    @requires_repo
    def tag_exists(self, tag_name: str) -> bool:
        """Check whether a tag with the given name exists."""
        if not tag_name:
            msg = 'Tag name is required'
            raise ValueError(msg)

        return (self.tags_dir() / tag_name).exists()

    @requires_repo
    def delete_branch(self, branch: str) -> None:
        """Delete a branch from the repository.

        :param branch: The name of the branch to delete.
        :raises ValueError: If the branch name is empty.
        :raises RepositoryError: If the branch does not exist or if it is the last branch in the repository.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        if not branch:
            msg = 'Branch name is required'
            raise ValueError(msg)
        branch_path = self.heads_dir() / branch

        if not branch_path.exists():
            msg = f'Branch "{branch}" does not exist.'
            raise RepositoryError(msg)
        if len(self.branches()) == 1:
            msg = f'Cannot delete the last branch "{branch}".'
            raise RepositoryError(msg)

        branch_path.unlink()

    @requires_repo
    def branch_exists(self, branch_ref: Ref) -> bool:
        """Check if a branch exists in the repository.

        :param branch_ref: The reference to the branch to check.
        :return: True if the branch exists, False otherwise.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        return (self.heads_dir() / branch_ref).exists()

    @requires_repo
    def branches(self) -> list[str]:
        """Get a list of all branch names in the repository.

        :return: A list of branch names.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        return [x.name for x in self.heads_dir().iterdir() if x.is_file()]

    @requires_repo
    def save_dir(self, path: Path) -> HashRef:
        """Save the content of a directory to the repository.

        :param path: The path to the directory to save.
        :return: A HashRef object representing the saved directory tree object.
        :raises NotADirectoryError: If the path is not a directory.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        if not path or not path.is_dir():
            msg = f'{path} is not a directory'
            raise NotADirectoryError(msg)

        stack = deque([path])
        hashes: dict[Path, str] = {}

        while stack:
            current_path = stack.pop()
            tree_records: dict[str, TreeRecord] = {}

            for item in current_path.iterdir():
                if item.name == self.repo_dir.name:
                    continue
                if item.is_file():
                    blob = self.save_file_content(item)
                    tree_records[item.name] = TreeRecord(TreeRecordType.BLOB, blob.hash, item.name)
                elif item.is_dir():
                    if item in hashes:  # If the directory has already been processed, use its hash
                        subtree_hash = hashes[item]
                        tree_records[item.name] = TreeRecord(TreeRecordType.TREE, subtree_hash, item.name)
                    else:
                        stack.append(current_path)
                        stack.append(item)
                        break
            else:
                tree = Tree(tree_records)
                save_tree(self.objects_dir(), tree)
                hashes[current_path] = hash_object(tree)

        return HashRef(hashes[path])

    @requires_repo
    def commit_working_dir(self, author: str, message: str) -> HashRef:
        """Commit the current working directory to the repository.

        :param author: The name of the commit author.
        :param message: The commit message.
        :return: A HashRef object representing the commit reference.
        :raises ValueError: If the author or message is empty.
        :raises RepositoryError: If the commit process fails.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        if not author:
            msg = 'Author is required'
            raise ValueError(msg)
        if not message:
            msg = 'Commit message is required'
            raise ValueError(msg)

        # See if HEAD is a symbolic reference to a branch that we need to update
        # if the commit process is successful.
        # Otherwise, there is nothing to update and HEAD will continue to point
        # to the detached commit.
        # Either way the commit HEAD eventually resolves to becomes the parent of the new commit.
        head_ref = self.head_ref()
        branch = head_ref if isinstance(head_ref, SymRef) else None
        parent_commit_ref = self.head_commit()

        # Save the current working directory as a tree
        tree_hash = self.save_dir(self.working_dir)

        commit = Commit(tree_hash, author, message, int(datetime.now().timestamp()), parent_commit_ref)
        commit_ref = HashRef(hash_object(commit))

        save_commit(self.objects_dir(), commit)

        if branch:
            # Extract the relative path from the SymRef (e.g., 'heads/feature' from SymRef('heads/feature'))
            ref_path = str(branch)
            self.update_ref(ref_path, commit_ref)

        return commit_ref

    @requires_repo
    def log(self, tip: Ref | None = None) -> Generator[LogEntry, None, None]:
        """Generate a log of commits in the repository, starting from the specified tip.

        :param tip: The reference to the commit to start from. If None, defaults to the current HEAD.
        :return: A generator yielding LogEntry objects representing the commits in the log.
        :raises RepositoryError: If a commit cannot be loaded.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        tip = tip or self.head_ref()
        current_hash = self.resolve_ref(tip)

        try:
            while current_hash:
                commit = load_commit(self.objects_dir(), current_hash)
                yield LogEntry(HashRef(current_hash), commit)

                current_hash = HashRef(commit.parent) if commit.parent else None
        except Exception as e:
            msg = f'Error loading commit {current_hash}'
            raise RepositoryError(msg) from e

    @requires_repo
    def diff_commits(self, commit_ref1: Ref | None = None, commit_ref2: Ref | None = None) -> Sequence[Diff]:
        """Generate a diff between two commits in the repository.

        :param commit_ref1: The reference to the first commit. If None, defaults to the current HEAD.
        :param commit_ref2: The reference to the second commit. If None, defaults to the current HEAD.
        :return: A list of Diff objects representing the differences between the two commits.
        :raises RepositoryError: If a commit or tree cannot be loaded.
        :raises RepositoryNotFoundError: If the repository does not exist."""
        if commit_ref1 is None:
            commit_ref1 = self.head_ref()
        if commit_ref2 is None:
            commit_ref2 = self.head_ref()

        try:
            commit_hash1 = self.resolve_ref(commit_ref1)
            commit_hash2 = self.resolve_ref(commit_ref2)

            if commit_hash1 is None:
                msg = f'Cannot resolve reference {commit_ref1}'
                raise RefError(msg)
            if commit_hash2 is None:
                msg = f'Cannot resolve reference {commit_ref2}'
                raise RefError(msg)

            commit1 = load_commit(self.objects_dir(), commit_hash1)
            commit2 = load_commit(self.objects_dir(), commit_hash2)
        except Exception as e:
            msg = 'Error loading commit'
            raise RepositoryError(msg) from e

        if commit1.tree_hash == commit2.tree_hash:
            return []

        try:
            tree1 = load_tree(self.objects_dir(), commit1.tree_hash)
            tree2 = load_tree(self.objects_dir(), commit2.tree_hash)
        except Exception as e:
            msg = 'Error loading tree'
            raise RepositoryError(msg) from e

        top_level_diff = Diff(TreeRecord(TreeRecordType.TREE, '', ''), None, [])
        stack = [(tree1, tree2, top_level_diff)]

        potentially_added: dict[str, Diff] = {}
        potentially_removed: dict[str, Diff] = {}

        while stack:
            current_tree1, current_tree2, parent_diff = stack.pop()
            records1 = current_tree1.records if current_tree1 else {}
            records2 = current_tree2.records if current_tree2 else {}

            for name, record1 in records1.items():
                if name not in records2:
                    local_diff: Diff

                    # This name is no longer in the tree, so it was either moved or removed
                    # Have we seen this hash before as a potentially-added record?
                    if record1.hash in potentially_added:
                        added_diff = potentially_added[record1.hash]
                        del potentially_added[record1.hash]

                        local_diff = MovedToDiff(record1, parent_diff, [], None)
                        moved_from_diff = MovedFromDiff(added_diff.record, added_diff.parent, [], local_diff)
                        local_diff.moved_to = moved_from_diff

                        # Replace the original added diff with a moved-from diff
                        added_diff.parent.children = (
                            [_ if _.record.hash != record1.hash
                             else moved_from_diff
                             for _ in added_diff.parent.children])

                    else:
                        local_diff = RemovedDiff(record1, parent_diff, [])
                        potentially_removed[record1.hash] = local_diff

                    parent_diff.children.append(local_diff)
                else:
                    record2 = records2[name]

                    # This record is identical in both trees, so no diff is needed
                    if record1.hash == record2.hash:
                        continue

                    # If the record is a tree, we need to recursively compare the trees
                    if record1.type == TreeRecordType.TREE and record2.type == TreeRecordType.TREE:
                        subtree_diff = ModifiedDiff(record1, parent_diff, [])

                        try:
                            tree1 = load_tree(self.objects_dir(), record1.hash)
                            tree2 = load_tree(self.objects_dir(), record2.hash)
                        except Exception as e:
                            msg = 'Error loading subtree for diff'
                            raise RepositoryError(msg) from e

                        stack.append((tree1, tree2, subtree_diff))
                        parent_diff.children.append(subtree_diff)
                    else:
                        modified_diff = ModifiedDiff(record1, parent_diff, [])
                        parent_diff.children.append(modified_diff)

            for name, record2 in records2.items():
                if name not in records1:
                    # This name is in the new tree but not in the old tree, so it was either
                    # added or moved
                    # If we've already seen this hash, it was moved, so convert the original
                    # added diff to a moved diff
                    if record2.hash in potentially_removed:
                        removed_diff = potentially_removed[record2.hash]
                        del potentially_removed[record2.hash]

                        local_diff = MovedFromDiff(record2, parent_diff, [], None)
                        moved_to_diff = MovedToDiff(removed_diff.record, removed_diff.parent, [], local_diff)
                        local_diff.moved_from = moved_to_diff

                        # Create a new diff for the moved record
                        removed_diff.parent.children = (
                            [_ if _.record.hash != record2.hash
                             else moved_to_diff
                             for _ in removed_diff.parent.children])

                    else:
                        local_diff = AddedDiff(record2, parent_diff, [])
                        potentially_added[record2.hash] = local_diff

                    parent_diff.children.append(local_diff)

        # Sort the diffs to ensure a deterministic order.
        # top_level_diff.children.sort(key=lambda d: d.record.name)

        return top_level_diff.children

    @requires_repo
    def common_ancestor(self, commit_ref1: Ref | None = None, commit_ref2: Ref | None = None) -> HashRef | None:
        """Find the common ancestor of two commits, if one exists."""
        if commit_ref1 is None:
            commit_ref1 = self.head_ref()
        if commit_ref2 is None:
            commit_ref2 = self.head_ref()

        try:
            commit_hash1 = self.resolve_ref(commit_ref1)
            commit_hash2 = self.resolve_ref(commit_ref2)

            if commit_hash1 is None:
                raise RefError(f'Cannot resolve reference {commit_ref1}')
            if commit_hash2 is None:
                raise RefError(f'Cannot resolve reference {commit_ref2}')
                
        except Exception as e:
            msg = 'Error resolving commit references'
            raise RepositoryError(msg) from e

        try:
            return find_common_ancestor_core(self.objects_dir(), commit_hash1, commit_hash2)
        except MergeError as e:
            msg = 'Error finding common ancestor'
            raise RepositoryError(msg) from e

    @requires_repo
    def merge_commits(self, commit_ref1: Ref | None = None, commit_ref2: Ref | None = None) -> MergeResult:
        """Perform a 3-way merge between two commits using their common ancestor."""
        if commit_ref1 is None and commit_ref2 is None:
            raise RepositoryError('Both commit references are None — nothing to merge')
        if commit_ref1 is None:
            commit_ref1 = self.head_ref()
        if commit_ref2 is None:
            commit_ref2 = self.head_ref()

        try:
            commit_hash1 = self.resolve_ref(commit_ref1)
            commit_hash2 = self.resolve_ref(commit_ref2)

            if commit_hash1 is None:
                raise RefError(f'Cannot resolve reference {commit_ref1}')
            if commit_hash2 is None:
                raise RefError(f'Cannot resolve reference {commit_ref2}')
        except Exception as e:
            msg = 'Error preparing commits for merge'
            raise RepositoryError(msg) from e

        try:
            return merge_commits_core(self.objects_dir(), commit_hash1, commit_hash2)
        except MergeError as e:
            msg = 'Error merging commits'
            raise RepositoryError(msg) from e


    def head_file(self) -> Path:
        """Get the path to the HEAD file within the repository.

        :return: The path to the HEAD file."""
        return self.repo_path() / HEAD_FILE


def branch_ref(branch: str) -> SymRef:
    """Create a symbolic reference for a branch name.

    :param branch: The name of the branch.
    :return: A SymRef object representing the branch reference."""
    return SymRef(f'{HEADS_DIR}/{branch}')


def tag_ref(tag: str) -> SymRef:
    """Create a symbolic reference for a tag name."""
    return SymRef(f'{TAGS_DIR}/{tag}')
