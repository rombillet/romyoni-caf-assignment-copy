# libcaf Module Overview

## repository.py

### Exceptions
- **RepositoryError** — Base exception for repository operations.
- **RepositoryNotFoundError(RepositoryError)** — Raised when the repo doesn't exist on disk.

### Data Classes
- **Diff** — Base diff record (record, parent, children).
- **AddedDiff, RemovedDiff, ModifiedDiff** — Diff subtypes for added/removed/modified entries.
- **MovedToDiff, MovedFromDiff** — Diff subtypes for moved entries (linked to each other).
- **LogEntry** — A commit hash + its Commit object.
- **Tag** — A tag name + the HashRef it points to.

### Repository Class

#### Setup & Paths
| Method | Description |
|---|---|
| `__init__(working_dir, repo_dir=None)` | Set paths; nothing created on disk yet. |
| `init(default_branch)` | Create repo dirs, default branch, and HEAD file. |
| `exists()` | Check if repo directory exists. |
| `repo_path()` | Path to `.caf/` directory. |
| `objects_dir()` | Path to `.caf/objects/`. |
| `refs_dir()` | Path to `.caf/refs/`. |
| `heads_dir()` | Path to `.caf/refs/heads/`. |
| `tags_dir()` | Path to `.caf/refs/tags/`. |
| `head_file()` | Path to `.caf/HEAD`. |
| `delete_repo()` | Remove the entire `.caf/` directory. |

#### Decorator
| Method | Description |
|---|---|
| `requires_repo(func)` | Static decorator — raises `RepositoryNotFoundError` if repo doesn't exist. |

#### Refs
| Method | Description |
|---|---|
| `head_ref()` | Read HEAD file, return current Ref (SymRef or HashRef). |
| `head_commit()` | Resolve HEAD to a HashRef (the current commit hash). |
| `refs()` | List all SymRefs under `refs/`. |
| `resolve_ref(ref)` | Recursively resolve a Ref/str/None to a HashRef. |
| `update_ref(ref_name, new_ref)` | Overwrite an existing ref file with a new value. |

#### Branches
| Method | Description |
|---|---|
| `add_branch(branch)` | Create an empty branch file under `refs/heads/`. |
| `delete_branch(branch)` | Remove a branch (blocks deleting the last one). |
| `branch_exists(branch_ref)` | Check if a branch file exists. |
| `branches()` | List all branch names. |

#### Tags
| Method | Description |
|---|---|
| `create_tag(tag_name, target)` | Create a tag pointing to a resolved commit. |
| `delete_tag(tag_name)` | Remove a tag file. |
| `list_tags()` | Return all tags sorted by name. |
| `tag_exists(tag_name)` | Check if a tag exists. |

#### Content & Commits
| Method | Description |
|---|---|
| `save_file_content(file)` | Hash and store a single file as a blob. |
| `save_dir(path)` | Recursively save a directory as tree objects; returns root HashRef. |
| `commit_working_dir(author, message)` | Snapshot working dir, create a Commit, update branch ref. |

#### History & Diffing
| Method | Description |
|---|---|
| `log(tip=None)` | Generator yielding LogEntry objects walking parent chain from tip. |
| `diff_commits(ref1, ref2)` | Compare two commits' trees; returns list of Diff objects (add/remove/modify/move). |

#### Merge
| Method | Description |
|---|---|
| `common_ancestor(ref1, ref2)` | Resolve refs then delegate to `find_common_ancestor_core`. |
| `merge_commits(ref1, ref2)` | Resolve refs then delegate to `merge_commits_core`. Returns MergeResult. |

### Module-level Helpers
| Function | Description |
|---|---|
| `branch_ref(branch)` | Build a SymRef like `heads/<branch>`. |
| `tag_ref(tag)` | Build a SymRef like `tags/<tag>`. |

---

## merge.py

### Exceptions
- **MergeError** — Base exception for merge operations.

### Data Classes
- **MergeResult** — Contains `tree_hash: HashRef` and `conflicts: list[str]`.

### Binary Detection
| Function | Description |
|---|---|
| `is_binary_blob(objects_dir, blob_hash, sample_size=8192)` | Read up to 8 KB of a blob; return True if null bytes found or >30% non-text bytes. |

### Line-level File Access
| Class / Function | Description |
|---|---|
| `MmapLineSequence(mmapped)` | Sequence wrapper over an mmap giving random access to lines by index. |
| `MmapLineSequence.build_line_index()` | Scan for `\n` positions to build the offset array. |
| `_open_line_sequence(stack, objects_dir, blob_hash)` | Open a blob, mmap it, build the line index, return the sequence. |

### Blob Merging
| Function | Description |
|---|---|
| `merge_blob_text(objects_dir, base, ours, theirs)` | 3-way text merge using `merge3`. Writes conflict markers (`<<<<<<<`/`=======`/`>>>>>>>`) on conflict. Returns (HashRef, conflict_bool). |
| `merge_blob_binary(objects_dir, base, ours, theirs)` | Pick a version for binary files: prefer fast-forward, fall back to ours, mark conflict if both sides changed. |
| `merge_blob(objects_dir, base, ours, theirs)` | Dispatch to `merge_blob_text` or `merge_blob_binary` based on `is_binary_blob`. |

### Tree Merging
| Function | Description |
|---|---|
| `_records_equal(a, b)` | None-safe equality check for TreeRecord. |
| `merge_trees_core(objects_dir, base_tree, ours_tree, theirs_tree, path_prefix, conflicts)` | Recursive 3-way tree merge. For each entry: skip if both sides agree, take theirs if ours unchanged, take ours if theirs unchanged, recurse into subtrees, merge blobs, or flag conflict. Returns merged tree HashRef. |

### Ancestor Search
| Function | Description |
|---|---|
| `find_common_ancestor_core(objects_dir, hash1, hash2)` | Walk hash1's parent chain into a set, then walk hash2's chain until a match is found. Returns HashRef or None. |

### Top-level Merge
| Function | Description |
|---|---|
| `merge_commits_core(objects_dir, ours_hash, theirs_hash)` | Find common ancestor, load all three trees, call `merge_trees_core`. Returns MergeResult. |

---

## How They Relate

```
Repository.merge_commits()          Repository.common_ancestor()
        |                                    |
   resolve refs                         resolve refs
        |                                    |
        v                                    v
merge_commits_core()                find_common_ancestor_core()
        |
        +---> find_common_ancestor_core()
        +---> load commits & trees
        +---> merge_trees_core()
                    |
                    +---> merge_blob()
                              |
                              +---> merge_blob_text()   (text files)
                              +---> merge_blob_binary() (binary files)
```

`repository.py` handles **ref resolution and error wrapping** (converting MergeError to RepositoryError).
`merge.py` contains the **pure merge logic** that operates on raw hashes and object paths.
