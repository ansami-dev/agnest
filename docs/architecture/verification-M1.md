# MVP1 NFR and Acceptance Verification Specification

**Status:** Proposed

**Owner:** Architecture / Integration (Codex)

**Issue:** #18

**Scope:** `FR-M1-001`–`FR-M1-020`, `NFR-M1-001`–`NFR-M1-007`, and the eight
acceptance scenarios in the MVP1 PRD

**Decisions:** `ADR-0003`, `ADR-0011`, `ADR-0013`

## 1. Purpose and gate semantics

This document turns MVP1 requirements into measurable contracts. It is the common input
to the implementation baseline, Data Design, Security, public API/RPC design, operations,
and the final Design Gate. It does not claim that documentation is executable evidence.

Two gates are deliberately distinct:

- **Design Ready** means every requirement has an owner, a testable oracle, named design
  evidence, and no unresolved dependency hidden as an assumption. Issue #28 applies this
  gate.
- **Release Ready** means implementations of the cases below passed on the supported
  reference appliance and their evidence is retained. Executable suites are engineering
  deliverables created after the Design Gate.

The words **must**, **must not**, and **required** are pass/fail conditions inherited
from the PRD or accepted ADRs. A numeric measurement always records the binary result,
raw value, fixture identity/version, appliance profile, Git/Incus/PostgreSQL/Agnest
versions, and correlation IDs. A skipped case passes only where this document explicitly
permits `NOT_SUPPORTED`; unavailable required infrastructure is `BLOCKED`, never `PASS`.

Case keys such as `AC-M1-01` and `NV-M1-01` are local anchors in this specification, not
new global artifact-ID families.

## 2. Evidence classes

| Evidence class | What it proves | Earliest gate |
|---|---|---|
| Document review | Required semantics, ownership, and cross-document consistency exist | Design Ready |
| Unit | Pure validation, state transition, revision, and policy logic | Release Ready |
| PostgreSQL integration | Constraints, transactions, leases, idempotency, migration, and restart persistence | Release Ready |
| Contract | OpenAPI/protobuf shape, compatibility, normalized errors, and adapter fixtures | Design schema at Design Ready; executable result at Release Ready |
| Security conformance | Denial, isolation, credential, mount, path, network, and privilege controls | Release Ready |
| Failure injection | Crash/timeout/lost-response behavior at a named effect boundary | Release Ready |
| End-to-end | User-observable workflow across API, database, Git, broker, Incus, and browser state | Release Ready |

## 3. NFR catalogue

The seven IDs below map one-to-one, in order, to the seven unnumbered clauses in MVP1
PRD §8. The measurement protocol makes each clause verifiable; it does not replace its
normative wording.

| ID | Normative requirement | Measurement and threshold | Failure evidence |
|---|---|---|---|
| `NFR-M1-001` | A Workspace created from a warm local mirror meets the 15-second target, excluding sandbox cold boot. | On the baseline reference appliance from Issue #19, run 3 unmeasured warm-ups and at least 30 measured serial creates from already-present pinned SHAs. Measure from accepted, durably identified request to usable Worktree plus committed `READY` projection. No fetch or sandbox provisioning is inside the interval. The p95 must be `<= 15.0 s`; report median, p95, maximum, and failures. | Timing samples, spans, fixture ID, and failed operation transitions. A functional failure never disappears from the performance sample set. |
| `NFR-M1-002` | Every Git state transition is idempotent or returns a recoverable conflict. | For every mutating Git operation, replay the same persisted intent and identical canonical input before response, after response, and after restart. It must produce at most one effect and the same terminal reference. Reusing the key with different canonical input, or using a stale expected revision, must return a typed non-retryable-without-change conflict and leave state unchanged. | Intent/transition rows, operation ID, before/after Git observations, normalized result, and absence of a second effect. |
| `NFR-M1-003` | Workspace operations tolerate process restart without losing canonical Git state. | Inject termination at every boundary between intent commit, effect dispatch, effect completion, observation, projection update, and response. After restart, reconciliation must converge within two completed reconciliation cycles when dependencies are observable. Git content/index/base SHA must be unchanged except for the intended effect. An unobservable effect remains explicitly blocked/unknown rather than guessed. | Failpoint, persisted intent history, pre/post Git object and revision evidence, reconciliation observations, projection version, and terminal or blocked reason. |
| `NFR-M1-004` | Sandbox resource limits are configurable. | At minimum, named server-owned profiles configure CPU, memory, and process-count limits independently. Two distinct configurations must be observable as their effective Incus values. A workload exceeding each enforced limit must be constrained or terminated with a normalized outcome. Optional disk/I/O controls are capability-reported; absence cannot be silently treated as enforcement. | Requested profile name, immutable capability snapshot, effective provider configuration, workload observation, and normalized limit outcome. |
| `NFR-M1-005` | Paths are normalized and protected against traversal. | Run the shared hostile-path corpus at every public API and internal adapter accepting paths: absolute paths, `..`, repeated/mixed separators, empty/NUL-invalid segments, symlink/junction escape, replaced parent, case/normalization alias where applicable, and path changed between validation and use. Every path that resolves outside the allocated root must be rejected before mutation; containment is revalidated at use time. | Encoded and decoded input class, allocated root identity, resolved target or safe rejection reason, effect counter proving no mutation, and `PATH_ESCAPE`/validation result without leaking host paths. |
| `NFR-M1-006` | Repositories much larger than one task's working set do not require complete contents in application memory. | The standard large-repository fixture contains at least 100,000 tracked paths and 10 GiB of Git objects, while the changed working set is at most 100 paths and all output caps are enabled. Status, bounded diff, and Workspace creation must stream/page metadata and never read complete repository file contents into the control-plane process. Peak control-plane RSS above its post-start idle baseline must be `<= 512 MiB`; response/blob bounds must hold. Git subprocess RSS is recorded separately and must fit the appliance budget selected in Issue #19. | Fixture manifest, process-separated RSS samples, response/blob byte counts, truncation/page markers, spans, and out-of-memory/timeout outcomes. |
| `NFR-M1-007` | Destructive Git operations require explicit API intent and an audit entry. | Restore/revert, discard, and any operation classified destructive must require authenticated actor, explicit operation ID, expected Workspace revision, and explicit path/scope or whole-Workspace confirmation. Intent and required audit evidence are durable before dispatch. Missing/invalid intent or failed audit append yields no effect. Replay produces neither a duplicate effect nor misleading duplicate completion evidence. | Authorization decision, intent/audit/transition correlation, expected revision and scope, dispatch counter, before/after Git observation, and failure-injection result. |

### 3.1 Interpretation boundaries

- `NFR-M1-001` uses p95 because the PRD states a performance **target**, not a hard
  per-sample deadline. The maximum remains visible. Product Owner acceptance of this
  interpretation is required on the Issue #18 PR.
- The reference appliance, exact tooling, and supported dependency versions are selected
  by Issue #19. That decision may make a fixture stricter but may not weaken the fixed
  `15 s`, containment, durability, or audit conditions above.
- The `512 MiB` value in `NFR-M1-006` bounds incremental control-plane memory, not the
  PostgreSQL, Incus, page cache, or Git subprocess budget. Those measurements are still
  reported separately so moving memory outside the process cannot masquerade as an
  optimization.
- Issues #20 and #21 select network and retention defaults. Tests may be authored before
  those decisions, but the final oracle must cite their accepted ADRs before Design Ready.

## 4. Product acceptance scenarios

Each scenario is a stable behavioral specification. Implementations may split one row
into multiple test executables, but the retained run must link every listed oracle.

### `AC-M1-01` — Connect Forgejo and fetch the default branch

**Covers:** `FR-M1-002`, `FR-M1-003`, `FR-M1-004`, `FR-M1-018`; `NFR-M1-002`,
`NFR-M1-003`.

**Given** a controlled Forgejo repository, a registered API origin, a separately bound
Git origin, and a read credential held only by the credentialed-fetch broker, **when** an
operator registers the repository and fetches its default branch, **then** normalized
metadata is persisted, the controlled per-Repository bare mirror contains the observed
commit, no active Worktree is mutated, and the Workspace base—when later created—is the
exact pinned SHA rather than a mutable branch name. Credential values and authenticated
URLs appear in no result, log, or sandbox.

**Executable evidence:** public API E2E; PostgreSQL integration; `CONF-M1-001`–`007`,
`030`, `033`; origin-redirect and lost-response failure injection.

### `AC-M1-02` — Create two isolated Workspaces from one SHA

**Covers:** `FR-M1-003`–`FR-M1-005`, `FR-M1-013`, `FR-M1-019`;
`NFR-M1-001`, `NFR-M1-002`, `NFR-M1-005`, `NFR-M1-006`.

**Given** a warm controlled mirror and one pinned base SHA, **when** two create requests
run concurrently, **then** they produce different Workspace IDs, branches, roots, index
state, and revisions while retaining the same base SHA. A tracked, staged, or untracked
change in one Workspace is absent from the other's status and diff. Each mutation is
serialized per Workspace without unnecessarily serializing the other Workspace.

**Executable evidence:** concurrency E2E; PostgreSQL uniqueness/race tests;
`CONF-M1-008`–`012`; latency run from `NV-M1-01`.

### `AC-M1-03` — Work locally in the required Incus system container

**Covers:** `FR-M1-005`–`FR-M1-007`, `FR-M1-010`–`FR-M1-017`, `FR-M1-020`;
`NFR-M1-002`, `NFR-M1-004`, `NFR-M1-005`, `NFR-M1-007`.

**Given** a healthy local Incus system-container profile and a READY Workspace, **when**
the operator starts its Sandbox, changes a file, executes a bounded command and named
test, reads status and a bounded file/hunk diff, and discards the Workspace, **then** all
runs/results carry the Workspace revision, exit/timing/output metadata is persisted,
the browser/API continuously identifies the work as local/unpublished, and the remote
repository remains unchanged. Only the assigned source projection and declared ephemeral
paths are writable; hidden Git metadata is reported rather than fabricated.

**Executable evidence:** browser/API/Incus E2E; `CONF-M1-013`–`025`, `030`, `032`,
`034`–`036`; resource, mount, credential, path, timeout, cancellation, and output-bound
security cases.

### `AC-M1-04` — Report optional Incus kinds without weakening required health

**Covers:** `FR-M1-008`, `FR-M1-009`; `NFR-M1-004`.

**Given** a host where the system-container baseline passes and one or both optional OCI
application-container/VM capability sets are incomplete, **when** capabilities and
provider health are evaluated, **then** each kind reports an immutable, independently
keyed result with every missing/unknown capability, system-container health remains
healthy, and create for an unsupported optional kind fails before an external effect.
An optional-kind execution test is `NOT_SUPPORTED`, not a skipped success.

**Executable evidence:** capability contract and live-smoke tests;
`CONF-M1-026`–`029`, `031`; cross-kind and stale-snapshot fixtures.

### `AC-M1-05` — Prove remote push authority is absent

**Covers:** `FR-M1-010`, `FR-M1-017`, `FR-M1-020`; `NFR-M1-005`.

**Given** a running default Sandbox attached to an unpublished Workspace, **when** a
repository-controlled process searches its environment, projected filesystem, Git
configuration, helper configuration, sockets, and reachable endpoints and then attempts
`git push`, **then** it obtains no remote-write credential or broker/daemon authority,
the push fails without remote mutation, and the API/browser still reports unpublished
local state. A network failure alone is insufficient proof; credential and authority
absence are independently asserted.

**Executable evidence:** security conformance and remote observation;
`CONF-M1-005`, `017`, `030`, `032`, `033`.

### `AC-M1-06` — Recover after control-plane restart

**Covers:** `FR-M1-004`–`FR-M1-006`, `FR-M1-016`, `FR-M1-018`, `FR-M1-019`;
`NFR-M1-002`, `NFR-M1-003`.

**Given** Workspaces in representative lifecycle states and one operation at each
persisted-intent/effect boundary, **when** the control plane is terminated and restarted,
**then** it reconstructs metadata from PostgreSQL and observes Git/Incus without changing
a pinned base, retargeting a stale generation, or redispatching an ambiguous operation.
Observable cases converge; unobservable cases remain explicitly blocking; foreign or
unpublished orphan resources are not destructively guessed away.

**Executable evidence:** failpoint matrix `NV-M1-03`; PostgreSQL restart integration;
`CONF-M1-006`, `007`, `012`, `015`, `016`, `018`, `022`, `023`, `029`, `035`, `036`.

### `AC-M1-07` — Revert safely and invalidate stale results

**Covers:** `FR-M1-012`–`FR-M1-015`; `NFR-M1-002`, `NFR-M1-005`, `NFR-M1-007`.

**Given** a dirty Workspace with a persisted diff and Test Run at revision R, **when** an
authorized operator explicitly restores one selected file at expected revision R,
**then** only that file changes, a new Workspace revision is produced, the prior diff and
Test Run remain historical but are marked stale for the new revision, and the destructive
intent/audit evidence precedes the effect. A stale revision, escaping path, or expanded
scope is rejected without mutation.

**Executable evidence:** API/Git/PostgreSQL E2E; `CONF-M1-009`–`011`; audit failure and
stale-revision injection.

### `AC-M1-08` — Destroy compute while preserving or archiving source

**Covers:** `FR-M1-005`, `FR-M1-006`, `FR-M1-016`; `NFR-M1-002`, `NFR-M1-003`,
`NFR-M1-007`.

**Given** a Workspace/Sandbox pair with positively observed ownership and generation,
**when** the operator chooses preserve or archive and destroys the Sandbox, **then**
provider compute is destroyed at most once while Workspace source follows the chosen
retention action. Ambiguous, foreign, stale-generation, or unpublished orphan state is
blocked/quarantined. The precise archive/retention duration and automatic-GC oracle must
cite the ADR produced by Issue #21 before this case can pass Design Ready.

**Executable evidence:** provider/Git/PostgreSQL E2E; `CONF-M1-012`, `015`, `016`,
`018`; lost-response and unavailable-authority failure injection.

## 5. Functional-requirement verification matrix

“Planned design” names the artifact that must exist by Issue #28; it is not evidence that
the artifact already exists.

| Requirement | Existing design evidence | Planned design dependency | Required executable evidence |
|---|---|---|---|
| `FR-M1-001` | `ADR-0013` control-plane/public-contract direction | Data #22; REST/UI #24 | Unit authorization/state tests; PostgreSQL CRUD/archive integration; public API and browser E2E |
| `FR-M1-002` | `ARC-M1-002`, `ARC-M1-004`; `INT-M1-001`, `INT-M1-002` | Data #22; Security #23; REST #24 | `AC-M1-01`; repository-host/fetch contract and credential-isolation tests |
| `FR-M1-003` | M1-I05–I07; `INT-M1-002`, `INT-M1-003` | Data #22; operations #27 | `AC-M1-01`, `AC-M1-02`; mirror concurrency, corruption, and restart tests |
| `FR-M1-004` | M1-I06; `INT-M1-001`, `INT-M1-003` | Data #22; REST #24 | Pinned-SHA PostgreSQL constraint and mutable-branch race tests |
| `FR-M1-005` | `ARC-M1-003`; M1-I06, I08–I10; `INT-M1-003`, `INT-M1-004` | Data #22; REST #24 | `AC-M1-02`, `AC-M1-03`; create idempotency, uniqueness, and partial-failure tests |
| `FR-M1-006` | `ARC-M1-005`, `ARC-M1-006`; `INT-M1-004`–`006` | Security #23; RPC #25 | Provider lifecycle/exec/capability contract suite and live Incus smoke tests |
| `FR-M1-007` | `ADR-0011`; `INT-M1-004`, `INT-M1-006` | Baseline #19; Security #23; RPC #25 | `AC-M1-03`; required system-container live conformance |
| `FR-M1-008` | `ADR-0011`; capability matrix; `INT-M1-004`, `INT-M1-006` | Security #23; RPC #25 | `AC-M1-04`; independently evidenced OCI capability tests or `NOT_SUPPORTED` |
| `FR-M1-009` | `ADR-0011`; capability matrix; `INT-M1-004`, `INT-M1-006` | Security #23; RPC #25 | `AC-M1-04`; nested-virtualization/VM capability tests or `NOT_SUPPORTED` |
| `FR-M1-010` | M1-I03, I07, I08, I11; `INT-M1-004` | Network ADR #20; Security #23 | `AC-M1-03`, `AC-M1-05`; mount/path/network/credential denial tests |
| `FR-M1-011` | M1-I12, I14, I24; `INT-M1-005` | Security #23; REST #24; RPC #25 | `AC-M1-03`; argv/env/cwd, timeout, cancellation, output, and unknown-outcome tests |
| `FR-M1-012` | M1-I10, I14, I15; `INT-M1-005` | Data #22; REST #24 | `AC-M1-03`, `AC-M1-07`; persisted Test Run and stale-revision tests |
| `FR-M1-013` | M1-I05, I08–I10; `INT-M1-003` | Data #22; REST #24 | `AC-M1-02`, `AC-M1-03`, `AC-M1-07`; porcelain edge-case fixtures |
| `FR-M1-014` | `INT-M1-003`; this specification | Data #22; REST #24 | `AC-M1-03`, `AC-M1-07`; base/HEAD file/hunk diff, binary, rename, bound, and stale tests |
| `FR-M1-015` | M1-I08–I10, I16; `INT-M1-003` | Security #23; REST #24 | `AC-M1-07`; stage/unstage/restore path, hunk, stale-revision, audit tests |
| `FR-M1-016` | `ARC-M1-003`, `ARC-M1-007`; `INT-M1-003`, `INT-M1-004` | Data state machines #22; REST #24 | Lifecycle transition/property tests; `AC-M1-06`, `AC-M1-08` |
| `FR-M1-017` | M1-I02, I03; `INT-M1-002`, `INT-M1-005` | Network ADR #20; Security #23 | `AC-M1-03`, `AC-M1-05`; secret/credential search and remote no-mutation evidence |
| `FR-M1-018` | M1-I06, I09, I16–I18; `INT-M1-001`–`003` | Data #22; REST #24 | Fetch-during-active-work, pinned-SHA, lost-response, and restart cases |
| `FR-M1-019` | M1-I03, I07, I09, I13; `INT-M1-003`, `INT-M1-004` | Data #22; Security #23 | `AC-M1-02`, `AC-M1-06`; concurrency/race and sibling-denial tests |
| `FR-M1-020` | `ADR-0013` browser/public-contract direction | Data publication fields #22; REST/UI #24 | Browser/API tests across READY, ACTIVE, DIRTY, STOPPED, ARCHIVED, and failed push states |

## 6. NFR verification protocols

These protocol anchors tell engineering how to turn the catalogue into repeatable suites.

| Case | Setup and perturbation | Required oracle | Primary evidence class |
|---|---|---|---|
| `NV-M1-01` | Warm-mirror creation fixture; 3 warm-ups plus 30 serial measurements | p95 `<= 15.0 s`, failures retained, measurement excludes fetch/sandbox | End-to-end/performance |
| `NV-M1-02` | Replay and conflicting reuse of every mutating Git operation ID, including after restart | At most one effect; stable terminal result; typed conflict with no mutation | Unit, PostgreSQL, Git integration |
| `NV-M1-03` | Kill at each persisted-intent/effect/observation/projection boundary | No canonical Git loss; observable convergence within two cycles; uncertainty stays blocked | PostgreSQL and failure injection |
| `NV-M1-04` | Apply two profiles and exceed CPU, memory, and process limits | Effective values differ as declared; each enforced limit constrains the workload | Provider/security conformance |
| `NV-M1-05` | Run hostile-path corpus plus validate/use replacement race at every path-bearing port | No escaped read/write/effect; stable safe error; no host-path leakage | Unit, contract, security conformance |
| `NV-M1-06` | Run create/status/bounded-diff on the standard 100k-path/10-GiB fixture | Control-plane RSS delta `<= 512 MiB`; bounded output; process-separated metrics | Performance/integration |
| `NV-M1-07` | Omit/alter intent fields, fail audit append, replay completed destructive intent | Rejected cases have zero effects; accepted case has correlated prior intent/audit and one effect | Authorization, PostgreSQL, failure injection |

## 7. Design Gate checklist and downstream handoff

Issue #28 may mark MVP1 Design Ready only when:

1. Issues #19–#27 are closed or their accepted outputs are present and linked.
2. Product Owner has accepted the p95 interpretation for `NFR-M1-001`.
3. Each row in §5 resolves to concrete schema/control/event/contract identifiers rather
   than only an issue number.
4. Security maps every applicable `THR-M1-*` to at least one `SEC-M1-*` and an
   executable case; Data maps every lifecycle oracle to legal transitions and events.
5. OpenAPI and protobuf schemas carry the idempotency, revision, generation, error,
   ownership, cancellation, and correlation fields required here.
6. Network and retention decisions are incorporated into `AC-M1-03`, `AC-M1-05`, and
   `AC-M1-08` without weakening accepted ADRs.
7. The operations runbook defines the reference appliance/fixture procedure and retained
   evidence locations.
8. The engineering backlog assigns implementation and automation of every `AC-M1-*`,
   `NV-M1-*`, and applicable `CONF-M1-*`; no documentation-only check is called a release
   pass.

The Integration conformance catalogue remains authoritative for `CONF-M1-*`. This
document composes those cases into product behavior and adds cross-component oracles; it
does not duplicate or renumber them.
