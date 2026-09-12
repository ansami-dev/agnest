# MVP1 architecture invariants

**Status:** Proposed  
**Owner:** Architecture (Codex)  
**Issue:** #7  
**Decision:** `ADR-0003`

These invariants are implementation constraints. `M1-Ixx` labels are local anchors for
tests and review; they are not globally allocated product IDs.

## Authority and dependency

### M1-I01 — Daemon authority is broker-only

Only `ARC-M1-005` has the provider daemon socket, group membership, or credential. The
control plane and task sandbox must start and operate without them.

### M1-I02 — Fetch credentials are broker-only and origin-bound

Only `ARC-M1-004` can resolve a fetch credential. A credential is selected from a
registered canonical `(scheme, host, effective port)` origin, never from caller-provided
credential material. User-info, unapproved schemes, origin mismatch, and cross-origin
redirects fail before credential transmission.

### M1-I03 — The task sandbox cannot reach control authority

The sandbox cannot access the mirror, linked-worktree Git administration, sibling
workspaces, application database/API, broker filesystem or network IPC, provider daemon,
control-plane secrets, or remote-write Git credentials. A provider profile that cannot
evidence these exclusions is ineligible.

### M1-I04 — Dependencies point inward through typed ports

The dependency direction is Control API → application use cases → domain ports →
adapters. Adapters cannot invoke use cases directly. The reconciler uses the same ports
and policy path as interactive requests.

## Git and Workspace

### M1-I05 — Git owns source state

The Git mirror and Workspace filesystem own commit, ref, index, and working-file truth.
The database stores identity, intent, lifecycle, and correlation; it never becomes a
second source of file truth.

### M1-I06 — A Workspace base is immutable

A Workspace records an exact base commit SHA at creation. Fetch may update mirror refs
but cannot move that base or mutate an active worktree.

### M1-I07 — Mirror and Workspace roots are separate

A sandbox receives only its Workspace projection. It never receives the mirror or the
linked-worktree `.git` indirection. Host-side Git operations remain in
`ARC-M1-003`.

### M1-I08 — Paths are contained at use time

Every control-plane file access resolves the real path immediately before use and rejects
an escape from the configured Workspace root. Tests include absolute paths, `..`,
symlink swaps, and relevant case-folding and Unicode behavior.

### M1-I09 — Workspace mutation is serialized

Git-mutating operations serialize per Workspace; mirror mutation serializes per
Repository. Concurrent Workspaces from one base are allowed because they share no
working-tree state.

### M1-I10 — Derived results carry a Workspace revision

Status, diff, Command Run, and Test Run results record the revision they describe. A
Workspace mutation makes earlier derived results stale; stale data is never returned as
current.

## Sandbox lifecycle and execution

### M1-I11 — Confinement is server-owned

The caller selects only a trusted profile name plus product identities. The provider
broker resolves image, user, mounts, devices, privileges, network policy, and limits.
It rejects a caller-provided raw provider specification.

### M1-I12 — Generation prevents stale retargeting

An `exec` or lifecycle request addresses `(sandbox_uuid, generation)`. A mismatch fails;
the operation is never redirected to the current generation.

### M1-I13 — At most one non-terminal sandbox exists per Workspace

Generation allocation, sandbox association insertion, and create-intent commit occur in
one transaction under the Workspace concurrency guard. A database uniqueness constraint
rejects a second non-terminal sandbox before any provider create call.

### M1-I14 — Execution is bounded and attributable

An execution request uses argv rather than an interpolated host-shell string, an approved
working directory revalidated at dispatch, an environment allowlist, timeout,
cancellation, and output bounds. Its result records sandbox generation, Workspace
revision, timestamps, exit/timeout state, and immutable output references.

### M1-I15 — Missing Git metadata is explicit

The Execution Gateway probes Git-metadata availability at sandbox start. Every affected
Command Run and Test Run carries `GitMetadataUnavailable`, including a zero-exit build
that generated fallback version data.

## Intent, observation, and reconciliation

### M1-I16 — Intent precedes every external effect

The fixed order is: commit intent → perform external action → observe result → record
outcome. If the intent cannot commit, the external action must not begin.

### M1-I17 — Idempotency belongs to one persisted intent

Retries reuse `operation_id`; a later user intent gets a new one. Provider identity is
`(deployment_id, workspace_id, generation, operation_id)` and is materialized as labels
or deterministic names. A retry observes before create.

### M1-I18 — Operation state and resource observation do not mix

`UNKNOWN_OUTCOME` describes an operation. `OBSERVED_PRESENT`, `OBSERVED_ABSENT`, and
`UNOBSERVABLE` describe a resource as seen by a named authority at a recorded time,
identity, and generation. An unavailable authority cannot prove absence.

### M1-I19 — Projection and journal cannot drift silently

The current-state projection and transition append share one transaction and one
structurally enforced write path. Each transition records the resulting projection
version, and a drift check can reconstruct and compare the expected projection.

### M1-I20 — Blocking guards are transactional

A transition requiring no unresolved blocking intent evaluates that predicate in the
same transaction as its update. Read-then-write enforcement is invalid.

### M1-I21 — Compensation is another intent

A compensation has its own operation ID and `compensates_operation_id`, and follows
M1-I16. The original becomes `COMPENSATED` only after the compensation reaches
`APPLIED`.

### M1-I22 — Destruction requires positive, repeated evidence

An owned provider orphan is stopped or quarantined before destruction. Automatic destroy
requires matching deployment ownership, positively available authorities, minimum age,
and a configured durable count of distinct successful observations. Restarts neither
erase nor manufacture evidence.

### M1-I23 — Unpublished work is preserved

A worktree without matching metadata is quarantined and surfaced to an operator; it is
never automatically deleted. A foreign or unlabeled provider resource is reported but
never mutated.

## Verification matrix

| Invariants | Primary verification |
|---|---|
| M1-I01–M1-I04 | Process identity/environment inspection, IPC authorization tests, sandbox network and mount denial tests, dependency-rule architecture test |
| M1-I05–M1-I10 | Git integration tests with two concurrent Workspaces, fetch during active work, path-escape fixtures, stale-result tests |
| M1-I11–M1-I15 | Provider conformance suite, hostile profile/request fixtures, stale-generation test, timeout/cancellation/output tests, zero-exit Git-version fallback fixture |
| M1-I16–M1-I21 | Database transaction tests, failpoint crash matrix, stop-start-stop identity test, projection drift injection, concurrency race tests |
| M1-I22–M1-I23 | Reconciliation tests across restart, unavailable volumes, foreign labels, observation thresholds, and unpublished orphan worktrees |

## Requirement traceability

| Requirement | Enforced primarily by |
|---|---|
| `FR-M1-002` | M1-I02, M1-I06, M1-I16 |
| `FR-M1-003` | M1-I05–M1-I07 |
| `FR-M1-005` | M1-I06, M1-I08–M1-I10 |
| `FR-M1-006` | M1-I11–M1-I15 |
| `FR-M1-010` | M1-I03, M1-I07, M1-I08, M1-I11 |
| `FR-M1-017` | M1-I02, M1-I03 |
| `FR-M1-018` | M1-I06, M1-I09, M1-I16–M1-I18 |
| `FR-M1-019` | M1-I03, M1-I07, M1-I09, M1-I13 |

## Deferred detail

Integration owns request/response schemas, authentication mechanism, health checks,
timeouts, capability matrices, and normalized error codes. Security owns threat/control
IDs and provider hardening baselines. Data Design owns entity schemas, legal state
transitions, field mutability, retention, and physical constraints. Those artifacts may
make these invariants more specific but cannot weaken them without a superseding ADR.
