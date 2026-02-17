from collections.abc import Callable
from pathlib import Path
from random import choice

from libcaf.repository import Repository
from pytest import CaptureFixture, FixtureRequest, TempPathFactory, fixture


def _random_string(length: int) -> str:
    return ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789-_') for _ in range(length)])


@fixture
def temp_repo_dir(tmp_path_factory: TempPathFactory) -> Path:
    return tmp_path_factory.mktemp('test_repo', numbered=True)


@fixture
def temp_repo(temp_repo_dir: Path) -> Repository:
    repo = Repository(working_dir=temp_repo_dir)
    repo.init()

    return repo


@fixture
def temp_content_length() -> int:
    return 100


@fixture
def temp_content(request: FixtureRequest, temp_content_length: int) -> tuple[Path, str]:
    factory = request.getfixturevalue('temp_content_file_factory')

    return factory(length=temp_content_length)


@fixture
def temp_content_file_factory(tmp_path_factory: TempPathFactory, temp_content_length: int) -> Callable[
    [str, int], tuple[Path, str]]:
    test_files = tmp_path_factory.mktemp('test_files')

    def _factory(content: bytes | str | None = None, length: int | None = None) -> tuple[Path, bytes | str]:
        if length is None:
            length = temp_content_length
        if content is None:
            content = _random_string(length).encode('utf-8')

        file = test_files / _random_string(10)
        with file.open('wb') as f:
            f.write(content)

        return file, content

    return _factory


@fixture
def parse_commit_hash(capsys: CaptureFixture[str]) -> Callable[[], str]:
    def _parse() -> str:
        out = capsys.readouterr().out

        commit_hash = None
        for line in out.splitlines():
            if line.startswith('Hash:'):
                commit_hash = line.split(':', 1)[1].strip()

        if commit_hash is None:
            msg = 'No hash found in output!'
            raise ValueError(msg)
        return commit_hash

    return _parse
