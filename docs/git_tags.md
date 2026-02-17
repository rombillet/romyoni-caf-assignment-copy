# Git-Style Tagging Reference

This document summarizes how Git tags behave and the aspects that are relevant
for the CAF tagging feature.

## What are tags?

- Tags are human-readable names that refer to a specific commit hash.
- Unlike branches, a tag does not move once it is created; it is an immutable
  alias that always resolves to the exact same commit.
- Tags also differ from commits: a commit stores a snapshot and metadata,
  while a tag is only a pointer to a commit (optionally annotated in Git, but
  lightweight in CAF).

## Common use cases

1. Releases – mark the commit that should be packaged or deployed.
2. Milestones – label important checkpoints such as demos or submissions.
3. Hotfix anchors – keep a stable pointer to a fix commit even if branches are
   later deleted.

## Storage model and commit relationship

- Git stores lightweight tags as files under `.git/refs/tags/<tag-name>`; the
  file only contains the commit hash the tag points to.
- CAF mirrors this structure using `.caf/refs/tags/<tag-name>`.
- Each tag file contains the hash of the target commit so resolving a tag is no
  different than resolving a branch reference: CAF reads the file, verifies the
  hash, and treats the tag as a `HashRef`.
