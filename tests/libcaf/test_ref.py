from pathlib import Path

from libcaf.constants import HASH_LENGTH
from libcaf.ref import HashRef, RefError, SymRef, read_ref, write_ref
from pytest import fixture, raises


def test_branch_name_with_slash() -> None:
    symref = SymRef('refs/heads/main')
    assert symref.branch_name() == 'main'


def test_branch_name_without_slash() -> None:
    symref = SymRef('main')
    assert symref.branch_name() == 'main'


def test_branch_name_multiple_slashes() -> None:
    symref = SymRef('refs/remotes/origin/feature-branch')
    assert symref.branch_name() == 'feature-branch'


@fixture
def ref_file(tmp_path: Path) -> Path:
    return tmp_path / 'ref'


def test_read_symbolic_ref(ref_file: Path) -> None:
    with ref_file.open('w') as f:
        f.write('ref: refs/heads/main')
        f.flush()

    result = read_ref(ref_file)
    assert isinstance(result, SymRef)
    assert result == 'refs/heads/main'


def test_read_empty_ref(ref_file: Path) -> None:
    with ref_file.open('w') as f:
        f.write('')
        f.flush()

    assert read_ref(ref_file) is None


def test_read_hash_ref(ref_file: Path) -> None:
    valid_hash = 'a' * HASH_LENGTH

    with ref_file.open('w') as f:
        f.write(valid_hash)
        f.flush()

    result = read_ref(ref_file)
    assert isinstance(result, HashRef)
    assert result == valid_hash


def test_read_ref_invalid_format_raises_error(ref_file: Path) -> None:
    with ref_file.open('w') as f:
        f.write('invalid reference content')
        f.flush()

    with raises(RefError):
        read_ref(ref_file)


def test_read_ref_invalid_hash_length(ref_file: Path) -> None:
    with ref_file.open('w') as f:
        f.write('abc123')  # Too short hash
        f.flush()

    with raises(RefError):
        read_ref(ref_file)


def test_read_ref_invalid_hash_characters(ref_file: Path) -> None:
    invalid_hash = 'g' * HASH_LENGTH  # 'g' is not a valid hex character

    with ref_file.open('w') as f:
        f.write(invalid_hash)
        f.flush()

    with raises(RefError):
        read_ref(ref_file)


def test_write_hash_ref(ref_file: Path) -> None:
    hash_ref = HashRef('a' * HASH_LENGTH)

    write_ref(ref_file, hash_ref)

    with ref_file.open() as f:
        content = f.read()
        assert content == hash_ref


def test_write_symbolic_ref(ref_file: Path) -> None:
    sym_ref = SymRef('refs/heads/main')

    write_ref(ref_file, sym_ref)

    with ref_file.open() as f:
        assert f.read() == 'ref: refs/heads/main'


def test_write_invalid_ref_type_raises_error(ref_file: Path) -> None:
    with raises(RefError):
        write_ref(ref_file, 123)
