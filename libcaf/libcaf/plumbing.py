"""Low-level plumbing functions for content-addressable storage."""

import os
from pathlib import Path
from typing import IO

import _libcaf
from _libcaf import Blob, Commit, Tree

from .ref import HashRef


def hash_file(filename: str | Path) -> str:
    if isinstance(filename, Path):
        filename = str(filename)

    return _libcaf.hash_file(filename)

def hash_object(obj: Blob | Commit | Tree) -> HashRef:
    return HashRef(_libcaf.hash_object(obj))

def hash_string(content: str) -> str:
    return _libcaf.hash_string(content)

def open_content_for_reading(root_dir: str | Path, hash_value: str) -> IO[bytes]:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    fd = _libcaf.open_content_for_reading(root_dir, hash_value)

    return os.fdopen(fd, 'rb')


def open_content_for_writing(root_dir: str | Path, hash_value: str) -> IO[bytes]:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    fd = _libcaf.open_content_for_writing(root_dir, hash_value)

    return os.fdopen(fd, 'wb')


def delete_content(root_dir: str | Path, hash_value: str) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    _libcaf.delete_content(root_dir, hash_value)


def save_file_content(root_dir: str | Path, file_path: str | Path) -> Blob:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    if isinstance(file_path, Path):
        file_path = str(file_path)

    return _libcaf.save_file_content(root_dir, file_path)


def save_commit(root_dir: str | Path, commit: Commit) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    _libcaf.save_commit(root_dir, commit)


def load_commit(root_dir: str | Path, commit_ref: HashRef) -> Commit:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    return _libcaf.load_commit(root_dir, commit_ref)


def save_tree(root_dir: str | Path, tree: Tree) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    _libcaf.save_tree(root_dir, tree)


def load_tree(root_dir: str | Path, hash_value: str) -> Tree:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    return _libcaf.load_tree(root_dir, hash_value)


__all__ = [
    'delete_content',
    'hash_file',
    'hash_object',
    'hash_string',
    'load_commit',
    'load_tree',
    'open_content_for_reading',
    'open_content_for_writing',
    'save_commit',
    'save_file_content',
    'save_tree',
]
