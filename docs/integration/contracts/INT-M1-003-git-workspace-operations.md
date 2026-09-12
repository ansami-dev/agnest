# INT-M1-003 — Git workspace operations

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Provider:** Native Git
**Requirements:** `FR-M1-003`–`FR-M1-005`, `FR-M1-013`–`FR-M1-015`, `FR-M1-018`, `FR-M1-019`

## Purpose and authority

This host-side contract is owned by the Git Workspace Service. It creates linked
worktrees from a controlled bare mirror and is the only path for status, diff, index
mutation, restore, quarantine, discard, and archive. Task sandboxes do not receive the
linked-worktree Git administration path.

This is an in-process domain port and host adapter, not a remotely callable endpoint.
Operator authentication and authorization are enforced by the Control API/application
use case before invocation; the adapter accepts only allocated product IDs and handles,
not caller-selected host paths. If extracted into another process later, it must adopt a
new authenticated transport decision rather than treating IDs as credentials.

## Locator rules

Callers use `repository_id` and `workspace_id`, never an arbitrary filesystem path. The
adapter resolves configured roots, follows the linked-worktree relationship, and repeats
real-path containment checks at the time of every access. Lexical prefix tests are not
sufficient. A missing/unmounted root is `UNOBSERVABLE` until root availability is proven.

## Operations

| Operation | Required inputs | Result / key rule |
|---|---|---|
| `create_workspace` | pinned base SHA, intended branch, operation ID | Creates one linked worktree under the allocated path; never resolves base by mutable branch at execution time. |
| `observe_workspace` | workspace ID | Presence, HEAD, branch, index/worktree summary, Git metadata condition, revision inputs. |
| `status` | workspace ID | Normalized tracked/staged/untracked/rename records without loading file bodies. |
| `diff` | workspace ID, comparison target, path filters, byte limit | Structured file/hunk metadata plus inline or blob-referenced content; explicit truncation. |
| `stage` | workspace ID, explicit paths/hunks, expected revision | Rejects stale revision and path escape; no implicit all-files mode. |
| `unstage` | workspace ID, explicit paths/hunks, expected revision | Preserves working-tree content and rejects stale revision. |
| `restore` | workspace ID, explicit paths/hunks, expected revision, destructive intent | Requires audit-backed explicit intent; never broadens paths. |
| `quarantine` | workspace ID or observed orphan locator | Makes an unowned worktree unavailable for automation while preserving content. |
| `discard` | workspace ID, expected revision, operation ID | Removes only positively owned metadata after lifecycle guards; orphaned unpublished work is never auto-deleted. |
| `archive` | workspace ID, expected revision | Preserves selected state according to retention policy and returns immutable references. |

All mutations serialize per Workspace. Mirror fetch serializes separately per Repository
and never operates in an active worktree.

## Workspace revision handoff

Every status, diff, Command Run, and Test Run is tagged with the Workspace revision it
describes. `HEAD` alone is forbidden: the revision must change with tracked content,
index state, and the untracked path/content set. Data Design owns the deterministic
algorithm and persistence fields; this adapter supplies the complete normalized inputs.

## Git error normalization

Index lock contention and stale expected revision are `CONFLICT`. An invalid object or
base SHA is `INVALID_ARGUMENT`; corrupt repository structure is `INTERNAL` with a
quarantine recommendation. Path escape is `PATH_ESCAPE`. Filesystem unavailability is
`UNOBSERVABLE`. User content is never copied into `safe_message`.

## Health

Health checks the Git version and required feature floor, mirror/workspace root
availability and permissions, and performs a read-only probe against a controlled fixture
repository. It never runs maintenance, fetch, checkout, or garbage collection.
