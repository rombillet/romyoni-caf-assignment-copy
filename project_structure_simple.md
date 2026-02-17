# Project Structure (Tree View)

```
romyoni-caf-assignment/
├── README.md — Top-level overview, quickstart, and architecture notes.
├── LICENSE — MIT license for reuse and distribution.
├── Makefile — Commands for Docker lifecycle, deployment, tests, and cleanup.
├── pyproject.toml — Workspace metadata plus pytest/Ruff settings.
├── .envrc — Sets `ENABLE_COVERAGE` via direnv when entering the repo.
├── .gitignore — Patterns for files Git should ignore.
├── .github/
│   └── workflows/
│       └── tests.yml — GitHub Actions workflow that runs the Makefile/CI pipeline.
├── assignment/
│   ├── asp26-assignment1.tex — LaTeX source for the assignment brief.
│   ├── artifacts/
│   │   └── asp26-assignment1.pdf — Prebuilt PDF of the assignment.
│   └── assets/ — Images and decorative resources used by the LaTeX document.
├── caf/
│   ├── pyproject.toml — Packaging info for the CLI (`caf` console script).
│   └── caf/
│       ├── __init__.py — (empty) package marker.
│       ├── __main__.py — Entry point that calls the CLI runner.
│       ├── cli.py — Builds the argparse CLI and dispatches commands.
│       └── cli_commands.py — Implementations of each CLI verb.
├── deployment/
│   └── Dockerfile — Builds the reproducible “caf-dev” development container.
├── libcaf/
│   ├── pyproject.toml — Packaging/build configuration for the native library.
│   ├── CMakeLists.txt — CMake build instructions for `_libcaf`.
│   ├── _libcaf.cpython-*.so — Compiled pybind11 extension exposing C++ features to Python.
│   ├── _libcaf.pyi — Type stubs describing the extension API.
│   ├── build/ — CMake build outputs (object files, caches, intermediate binaries).
│   ├── libcaf/
│   │   ├── __init__.py — Re-exports Blob/Tree/Commit symbols from `_libcaf`.
│   │   ├── constants.py — Shared constants for repo layout and hashing.
│   │   ├── plumbing.py — Python wrappers around native hashing/storage helpers.
│   │   ├── ref.py — Reference types and read/write helpers for branch/commit refs.
│   │   └── repository.py — High-level repository API (init, commit, branches, diff, log).
│   └── src/
│       ├── bind.cpp — pybind11 bridge exposing the C++ code to Python.
│       ├── caf.cpp / caf.h — Hashing, blob storage, and file-locking implementation.
│       ├── blob.h — C++ Blob object definition.
│       ├── commit.h — C++ Commit object definition.
│       ├── tree.h — C++ Tree object definition.
│       ├── tree_record.h — Entry metadata for trees.
│       ├── hash_types.cpp / hash_types.h — `hash_object` helpers for blobs/trees/commits.
│       └── object_io.cpp / object_io.h — Serialize/deserialize commits and trees.
├── tests/
│   ├── conftest.py — Shared pytest fixtures for temp repos and helpers.
│   ├── caf/
│   │   └── cli_commands/
│   │       ├── test_add_branch_command.py — Tests for `caf add_branch`.
│   │       ├── test_branch_command.py — Tests for `caf branch`.
│   │       ├── test_branch_exists_command.py — Tests for `caf branch_exists`.
│   │       ├── test_commit_command.py — Tests for `caf commit`.
│   │       ├── test_delete_branch_command.py — Tests for `caf delete_branch`.
│   │       ├── test_delete_repo_command.py — Tests for `caf delete_repo`.
│   │       ├── test_diff_command.py — Tests for `caf diff`.
│   │       ├── test_hash_file_command.py — Tests for `caf hash_file`.
│   │       ├── test_init_command.py — Tests for `caf init`.
│   │       └── test_log_command.py — Tests for `caf log`.
│   └── libcaf/
│       ├── test_content.py — Verifies blob storage operations.
│       ├── test_diff.py — Validates the diff data structures and logic.
│       ├── test_hashing.py — Ensures hash helpers behave as expected.
│       ├── test_object_io.py — Tests commit/tree serialization and locking.
│       ├── test_objects.py — Covers Blob/Tree/TreeRecord shapes.
│       ├── test_ref.py — Tests reference parsing/writing.
│       └── test_repository.py — End-to-end repository behavior tests.
├── task1.md — Detailed catalog/analysis for the assignment’s first task.
├── stupidprogex.md — Kid-friendly explanation of CAF using a librarian/robot story.
└── project_structure_simple.md — This tree-style quick reference.
```
