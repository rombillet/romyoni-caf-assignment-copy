"""Reference objects and operations."""

from pathlib import Path

from .constants import HASH_CHARSET, HASH_LENGTH


class RefError(Exception):
    """Exception raised for reference-related errors."""


class HashRef(str):
    """A reference that directly points to a commit hash."""

    __slots__ = ()


class SymRef(str):
    """A symbolic reference that may point to another reference."""

    __slots__ = ()

    def branch_name(self) -> str:
        """Extract the branch name from a symbolic reference."""
        return self.split('/')[-1] if '/' in self else self


Ref = HashRef | SymRef | str


def read_ref(ref_file: Path) -> Ref | None:
    """Read a reference from a file.

    :param ref_file: Path to the reference file
    :return: A Ref object (HashRef or SymRef) or None if the file is empty
    :raises RefError: If the reference format is invalid"""
    with ref_file.open() as f:
        content = f.read().strip()

        if content.startswith('ref:'):
            return SymRef(content.split(': ')[-1])

        if not content:
            return None

        if len(content) == HASH_LENGTH and all(c in HASH_CHARSET for c in content):
            return HashRef(content)

        msg = f'Invalid reference format in ref file {ref_file}!'
        raise RefError(msg)


def write_ref(ref_file: Path, ref: Ref) -> None:
    """Write a reference to a file.

    :param ref_file: Path to the reference file
    :param ref: Reference to write (HashRef or SymRef)
    :raises RefError: If the reference type is invalid"""
    with ref_file.open('w') as f:
        match ref:
            case HashRef():
                f.write(ref)
            case SymRef(ref):
                f.write(f'ref: {ref}')
            case _:
                msg = f'Invalid reference type: {type(ref)}'
                raise RefError(msg)
