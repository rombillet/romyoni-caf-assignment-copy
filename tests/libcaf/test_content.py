import hashlib
from pathlib import Path

from libcaf.plumbing import (delete_content, hash_file, open_content_for_reading, open_content_for_writing,
                             save_file_content)
from pytest import mark, raises


class TestNonExistentContent:
    def test_open_non_existent_file(self, temp_repo_dir: Path) -> None:
        non_existent_hash = 'deadbeef' + '0' * 32

        with raises(RuntimeError):
            open_content_for_reading(temp_repo_dir, non_existent_hash)

    def test_delete_non_existent_file(self, temp_repo_dir: Path) -> None:
        non_existent_hash = 'deadbeef' + '0' * 32
        delete_content(temp_repo_dir, non_existent_hash)


@mark.parametrize('temp_content_length', [0, 1, 10, 100, 1000, 10000, 100000, 1000000])
class TestContent:
    def test_hash_file(self, temp_content: tuple[Path, str]) -> None:
        file, content = temp_content

        actual = hash_file(file)
        expected = hashlib.sha1(content).hexdigest()

        assert actual == expected

    def test_save_file_content(self, temp_repo_dir: Path, temp_content: tuple[Path, str]) -> None:
        file, expected_content = temp_content

        blob = save_file_content(temp_repo_dir, file)

        saved_file = temp_repo_dir / f'{blob.hash[:2]}/{blob.hash}'
        assert saved_file.exists()

        saved_content = saved_file.read_bytes()
        assert saved_content == expected_content

    def test_open_content_for_reading(self, temp_repo_dir: Path, temp_content: tuple[Path, str]) -> None:
        file, expected_content = temp_content

        blob = save_file_content(temp_repo_dir, file)

        with open_content_for_reading(temp_repo_dir, blob.hash) as f:
            saved_content = f.read()

        assert saved_content == expected_content

    def test_open_content_for_writing(self, temp_repo_dir: Path, temp_content: tuple[Path, str]) -> None:
        file, expected_content = temp_content

        blob = save_file_content(temp_repo_dir, file)

        with open_content_for_writing(temp_repo_dir, blob.hash) as f:
            f.write(expected_content)

        saved_file = temp_repo_dir / f'{blob.hash[:2]}/{blob.hash}'
        saved_content = saved_file.read_bytes()

        assert saved_content == expected_content

    def test_save_and_delete_content(self, temp_repo_dir: Path, temp_content: tuple[Path, str]) -> None:
        file, _ = temp_content

        blob = save_file_content(temp_repo_dir, file)

        saved_file_path = temp_repo_dir / f'{blob.hash[:2]}/{blob.hash}'
        assert saved_file_path.exists()

        delete_content(temp_repo_dir, blob.hash)
        assert not saved_file_path.exists()
