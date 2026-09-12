# ADR-0003: Enforce three authority boundaries around the MVP1 modular control plane

| | |
|---|---|
| **Status** | Proposed |
| **Originating issue** | #3 |
| **Supersedes** | none |
| **Deciders** | Architecture, Integration, Security, Data Design |
| **Coordinator** | Architecture (Codex) |
| **Date** | 2026-09-13 |
| **MVP** | MVP1 — Git Foundation & Sandboxed Workspaces |
| **Requirements** | `FR-M1-002`, `FR-M1-003`, `FR-M1-005`, `FR-M1-006`, `FR-M1-010`, `FR-M1-017`, `FR-M1-018`, `FR-M1-019` |

## Context

MVP1 must create isolated Git worktrees, provision Docker or LXC/Incus sandboxes,
execute commands, fetch remote changes, and recover after partial failure. These actions
do not carry equal authority:

- a sandbox processes repository-controlled and user-controlled content;
- unrestricted Docker or Incus daemon access is effectively host-level authority;
- repository credentials grant external authority and must not reach repository content
  processing or the task sandbox;
- Git, the relational database, the filesystem, and a sandbox provider cannot share one
  atomic transaction.

Putting all of this authority in the API process would turn ordinary input-handling bugs
into host or credential compromise. Splitting every logical component into a service,
however, would add deployment and failure complexity without improving containment.

The decision therefore needs to distinguish authority boundaries, which require process
and operating-system isolation, from module boundaries, which primarily preserve design
and testability. It also needs to make recovery deterministic without treating cached
metadata or provider identifiers as canonical product state.

This decision follows the product principles that Git remains canonical for repository
state, sandboxes remain replaceable, credentials stay outside the default agent sandbox,
and active workspaces remain pinned to an immutable base commit.

## Decision

### 1. Deploy one modular control plane behind three authority boundaries

MVP1 uses one control-plane deployable containing explicit modules, plus two privileged
broker processes and the untrusted task sandbox:

```text
Operator / local UI
        |
        v
+---------------------- Control-plane process -----------------------+
| Control API -> application use cases -> typed domain ports          |
|                                                                    |
| Repository metadata     Git Workspace Service     Execution Gateway |
| Intent journal/store    Reconciler                Blob references   |
+-----------+----------------------+----------------------+------------+
            |                      |                      |
            | authenticated IPC    | host filesystem      | authenticated IPC
            v                      v                      v
  +-------------------+   separate mirror/workspace   +-------------------+
  | Credentialed-fetch|          roots               | Sandbox-provider  |
  | broker process    |                              | broker process    |
  +---------+---------+                              +---------+---------+
            |                                                  |
       fetch-only secret                                  daemon authority
            |                                                  |
            v                                                  v
      remote Git host                                  untrusted task sandbox
```

The three authority boundaries are:

1. **Task sandbox versus everything else.** The sandbox is the untrusted execution
   boundary and receives access only to its projected workspace and explicitly declared
   ephemeral paths.
2. **Sandbox-provider broker versus the control plane.** Only the broker holds Docker or
   Incus daemon authority. It runs as a separate process with a distinct OS identity.
3. **Credentialed-fetch broker versus repository content processing.** Only this broker
   can use a repository fetch credential. It performs the fetch and never returns a
   reusable secret to the control plane.

The component IDs established by this decision are:

| ID | Component | MVP1 deployment |
|---|---|---|
| `ARC-M1-001` | Modular control plane | Control-plane process |
| `ARC-M1-002` | Repository service | Control-plane module |
| `ARC-M1-003` | Git workspace service | Control-plane module |
| `ARC-M1-004` | Credentialed-fetch broker | Separate process and OS identity |
| `ARC-M1-005` | Sandbox-provider broker | Separate process and OS identity |
| `ARC-M1-006` | Execution gateway | Control-plane module |
| `ARC-M1-007` | Recovery reconciler | Control-plane module |
| `ARC-M1-008` | Task sandbox boundary | Provider-created untrusted process/container/VM |

Control API and application use cases live in `ARC-M1-001`; repository metadata belongs
to `ARC-M1-002`; transition persistence and blob references are control-plane adapters.
Their ports remain transport-neutral so a later ADR can extract them without changing
domain callers.

The allowed dependency direction is:

```text
Control API -> application use cases -> domain ports -> adapters
```

Adapters return observations and typed failures. They do not invoke application use
cases directly. Interactive operations and reconciliation use the same domain ports,
policy checks, concurrency controls, and audit path.

### 2. Restrict authority by component

| Component | May hold or access | Must not hold or access |
|---|---|---|
| Control plane | Application database, workspace root through `GitWorkspaceService`, typed broker clients | Git credentials, provider daemon socket or credentials, arbitrary sandbox host paths |
| Credentialed-fetch broker | Fetch-only credential, configured mirror root, explicit remote URL | Workspace roots, application database, sandbox daemon, reusable credential export |
| Sandbox-provider broker | Provider daemon authority, trusted profile catalogue, broker-owned resource mapping | Repository credentials, application database, caller-supplied container specifications |
| Task sandbox | Assigned workspace projection, declared ephemeral paths, profile-approved network destinations | Bare mirror, linked-worktree Git administration, sibling workspaces, control-plane API/database, control-plane-to-broker IPC endpoints, provider daemon, control-plane secrets, remote-write Git credentials |

The two brokers communicate with the control plane over authenticated local IPC on the
sandbox host. Unix-domain sockets with peer and filesystem permissions are the Linux
baseline; another host OS must provide an equivalent peer-authenticated local transport.
The control-plane identity is not a member of the Docker group and receives no provider
daemon credential.

Broker socket paths are outside every sandbox-visible mount root. If a broker uses a
local network endpoint rather than a filesystem socket, sandbox network policy denies
that endpoint. A profile cannot override either exclusion.

### 3. Make bare mirror plus isolated worktrees an invariant

Each registered repository has a controlled bare mirror. Credentialed updates fetch into
that mirror; they never fetch into an active worktree. Mirror mutation is serialized per
repository, and an update cannot change the base commit recorded by an existing
workspace.

Mirror and workspace roots are separate. Concurrent workspaces may share Git objects on
the host but never working-tree state. Each workspace has an immutable internal UUID and
records its exact base commit SHA; neither its path nor its branch name is its identity.

The host-side workspace remains a linked Git worktree. The task sandbox receives a
projection where the linked-worktree `.git` indirection is hidden behind an inert,
read-only mount. It cannot see the mirror or shared worktree administration data. Git
status, diff, stage, unstage, revert, and other Git mutations execute through the
host-side `GitWorkspaceService`.

Control-plane reads resolve the real path at the time of access and reject any result
outside the assigned workspace root. A prior lexical-prefix check is insufficient because
the writable workspace may contain symlinks and may change between validation and use.

Hiding `.git` means tools such as `git describe`, `setuptools_scm`, `hatch-vcs`, Git-aware
Gradle or Maven plugins, `vergen`, and repository-specific build scripts can fail or
produce fallback version data inside the sandbox. MVP1 reports this limitation rather
than silently presenting an incorrect build as fully representative. Providing a
read-only workspace-scoped Git view is deferred to the runtime-boundary decision before
MVP2; exposing the mirror is not an acceptable workaround.

The projection mechanism alone is not the diagnostic mechanism: an absent and a masked
or invalid `.git` entry can produce different tool behavior. At sandbox start, the
Execution Gateway probes whether workspace Git metadata is available and records the
result. Every command and test result from the MVP1 projection carries an explicit
`GitMetadataUnavailable` environment condition when it is not. A zero-exit build may
still succeed, but Agnest does not present it as fully representative without that
warning.

### 4. Keep provider confinement server-owned

The sandbox-provider broker owns a versioned profile catalogue. A create request carries
only trusted product identities, `generation`, `deployment_id`, and a profile name. The
broker resolves the image, runtime user, workspace mapping, mounts, devices, privileges,
network policy, resource limits, and provider-specific configuration. It never accepts a
raw Docker, Incus, or VM specification from the caller.

The profile catalogue treats the control-plane-to-broker IPC paths as reserved host
paths that cannot be mounted or exposed to a task sandbox. For network IPC, the profile
must also exclude the endpoint from allowed routes. Profile validation fails closed when
either exclusion cannot be evidenced by the provider.

Provider capabilities include security properties as well as lifecycle operations:
rootless or user-namespace support, read-only and masked mounts, network isolation,
seccomp and capability controls, resource limits, guest execution, cancellation, and
ownership labels. An unknown capability is treated as unsupported. A profile is eligible
only when the provider evidences every capability the profile requires.

For MVP1, `exec` may traverse the typed broker interface because `FR-M1-006` requires it.
Command content is data inside an already-established confinement; callers cannot vary
the confinement itself. An execution request:

- targets `(sandbox_uuid, generation)` under an existing lease;
- is rejected, never retargeted, when the generation is stale;
- carries argv rather than an interpolated host-shell command;
- uses an allowlisted environment, bounded output, timeout, and cancellation;
- resolves and revalidates the approved working directory at execution time.

Before MVP2 runtime adapters make execution continuous and agent-driven, a new decision
must evaluate moving high-frequency execution to an authenticated, unprivileged guest
executor so the daemon-authority process leaves the command hot path.

### 5. Execute authenticated fetch inside its broker

The control plane requests an authenticated fetch operation; it does not request a
credential value or credential handle usable elsewhere. The credentialed-fetch broker
uses a short-lived, operation-scoped credential against an explicit registered remote URL
and writes only to the configured mirror root.

Each credential is bound to an allowed canonical origin: scheme, host, and effective
port. The broker selects the credential from that origin rather than from caller input,
rejects URLs containing user information or an origin mismatch, and permits only schemes
declared by the integration. It does not follow a cross-origin redirect with or without
the credential; a redirected origin must be registered and fetched as a separate
operation under its own credential policy.

The fetch environment uses sanitized Git configuration: hooks are disabled, dangerous
protocols such as `protocol.ext` are denied, submodules are not recursively fetched, and
repository-local credential helpers are not used for authentication. No process that
later operates on checked-out repository content inherits the credential.

### 6. Assign one canonical owner to each fact

| Fact | Canonical authority |
|---|---|
| Repository files, refs, object graph, index, working tree, base SHA | Git and the host filesystem |
| Agnest identity, desired state, intent, lifecycle history, ownership, correlation | Relational metadata store |
| Whether a sandbox or other provider resource currently exists | Provider observation |
| Logs and large diffs | Immutable blobs referenced by metadata |

Provider resource IDs and filesystem paths are references, not product identities.
Cached status or diff data records the workspace revision it describes and is invalid
once that revision changes. No component silently reconstructs one canonical domain from
another when the relationship is ambiguous; it records an unknown outcome for
reconciliation.

### 7. Journal intent before every cross-boundary action

No transaction spans the database, Git filesystem, and sandbox provider. Every external
operation therefore follows this order:

```text
commit intent -> perform external action -> observe result -> record outcome
```

The persisted intent owns a unique `operation_id`. Retries of the same intent reuse it;
a later user request receives a new one. Provider idempotency is scoped by:

```text
(deployment_id, workspace_id, generation, operation_id)
```

Docker and Incus do not provide an application idempotency-key facility, so the broker
materializes this identity through provider labels and/or deterministic resource names.
A retry observes by that identity and creates only when absent.

Each external-operation intent has one of `PENDING`, `APPLIED`, `UNKNOWN_OUTCOME`,
`RECONCILING`, `FAILED`, or `COMPENSATED`. Ambiguity belongs to the affected operation or
resource rather than a single workspace lifecycle state. The UI may derive a
`RecoveryPending` or “Reconciling” condition, but that derived condition is not an
enforcement boundary.

`COMPENSATED` means a separate compensation intent reached `APPLIED`. The compensation
has its own `operation_id`, follows the same intent-before-action sequence, and links to
the original through `compensates_operation_id`. The original intent cannot be marked
`COMPENSATED` merely because an application handler attempted cleanup.

Resource observation uses a separate vocabulary:

- `OBSERVED_PRESENT` — a positively available authority reports the resource;
- `OBSERVED_ABSENT` — that authority is positively available and confirms absence;
- `UNOBSERVABLE` — the authority is unavailable or the observation is inconclusive.

`UNKNOWN_OUTCOME` describes an operation whose result is ambiguous; it is never reused
as a resource-presence condition. Observations record their authority, time, resource
identity, and generation.

The current-state projection and its append-only transition row are written in one
database transaction through one structurally enforced write path. Each transition row
records the projection version it produced so drift can be detected. This is not a
requirement for full event sourcing.

A lifecycle transition that requires “no blocking unresolved intent” evaluates that
predicate atomically in the same transaction as its update. An application-level read
followed by a separate write is prohibited because it introduces a time-of-check to
time-of-use race.

A workspace has at most one non-terminal sandbox binding. The next sandbox `generation`
is allocated while holding the workspace's concurrency guard, in the same transaction
that inserts the non-terminal binding and commits its create intent. A database
constraint, such as a partial unique index over non-terminal bindings by `workspace_id`,
makes a competing user or reconciler allocation fail before either can create a second
provider resource.

### 8. Reconcile conservatively and preserve unpublished work

The reconciler compares committed intent with positively available filesystem and
provider observations. It applies these minimum resolutions:

| Observation | Resolution |
|---|---|
| Intent exists; expected provider resource is absent | Retry by persisted intent when safe, create a new generation when replacement is required, or fail explicitly |
| Provider resource has no intent but carries this deployment's ownership labels | Stop or quarantine first; destroy only after both a minimum grace period and a configured number of distinct successful observations |
| Provider resource has foreign or missing ownership labels | Report; never mutate automatically |
| Metadata references a worktree that appears absent | Record `UNOBSERVABLE` until the workspace root is positively available; only then may a new observation confirm `OBSERVED_ABSENT` |
| Worktree exists without matching metadata | Quarantine and surface for operator recovery; never delete automatically |
| Resource identity or generation conflicts | Block mutation and require reconciliation or operator resolution |

The repeated-observation count is durable and survives restarts. A restart is not
required to advance it, and wall-clock age alone is never sufficient evidence for
destruction. This prevents the first sweep after a long outage from deleting an estate
whose authoritative stores may still be recovering.

Git mutation is serialized per workspace. External lifecycle operations use expected
state or projection versions; stale callers receive a recoverable conflict rather than
overwriting newer state.

## Consequences

### Architecture

- MVP1 operates three deployable trust domains even though most product capabilities
  remain a modular monolith.
- Domain code depends on typed ports and least-authority handles, not a shared service
  container containing credentials or daemon clients.
- The guest-executor decision is a required architecture gate before MVP2 runtime
  adapters, not an optional optimization.

### Integration

- Docker and Incus adapters live behind the broker and must prove declared isolation
  capabilities rather than rely on a falsely uniform provider contract.
- Local IPC, OS identities, provider ownership labels, sanitized Git execution, and
  observe-before-create behavior become integration requirements.
- Windows or remote providers must supply a peer-authenticated transport and equivalent
  path-containment guarantees rather than inherit Unix assumptions.

### Security

- Compromise of the control API does not directly confer provider-daemon or repository
  credential authority.
- The sandbox has no route to shared Git administration, sibling workspaces,
  control-plane state, or remote-write credentials by default.
- The broker boundary reduces authority concentration but does not replace provider
  hardening; exact Docker, LXC/Incus, network, and syscall profiles remain separate work.

### Data Design

- Workspace and sandbox identities are internal UUIDs. A sandbox binding additionally
  records a workspace-scoped generation and provider reference.
- Intent, projection version, transition history, ownership labels, and durable
  reconciliation observations are first-class persisted data.
- Database schemas must make projection-only mutation and non-atomic blocking guards
  structurally impossible or detectably invalid.

### Product and operations

- MVP1 has more local processes and OS identities to install, start, monitor, and
  upgrade than a single-process prototype.
- Recovery favors preserving evidence and unpublished work over eager cleanup, so some
  ambiguous resources require operator attention.
- Builds that depend on Git metadata inside the sandbox may degrade until a scoped Git
  read interface is decided and implemented.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| One process containing API, credentials, and provider daemon access | An input-handling compromise would inherit both external credential authority and host-equivalent daemon authority. Typed modules alone do not contain that compromise. |
| A microservice for every logical component | It adds network, deployment, and distributed-failure cost without changing authority for control-plane modules that share the same trust level. |
| Give Repository Service a reusable credential or token | It expands credential exposure into components that process repository-controlled state and makes accidental sandbox inheritance more likely. |
| Let the provider broker accept arbitrary container specifications | It creates a confused deputy: an unprivileged caller can ask the privileged broker to construct attacker-selected confinement. |
| Mount the linked worktree, including `.git`, directly in the sandbox | Linked-worktree metadata points into shared Git administration and can expose or mutate state across workspace boundaries. |
| Clone separately inside every sandbox | It weakens centralized fetch credential custody, duplicates Git data, and abandons the PRD's host-managed mirror/worktree model. |
| Add `RECONCILING` as one workspace lifecycle state | Different worktree, sandbox, mount, and execution operations can be ambiguous simultaneously; one state collapses independent facts. |
| Treat the journal as the only read model | Full event sourcing is unnecessary for MVP1. A transactionally maintained projection provides simpler invariant checks and queries while the journal preserves audit and recovery evidence. |
| Derive idempotency only from workspace, generation, and operation type | A valid repeated operation such as stop-start-stop would collide with its earlier intent. |
| Delete apparent orphans after elapsed time alone | After an outage, age does not establish ownership or authoritative absence and could trigger mass deletion during incomplete recovery. |

## Deferred decisions

These are outside the originating issue's scope and do not represent disagreement:

- exact database schema and migration technology;
- exact IPC protocol and provider implementation;
- final Docker and LXC/Incus hardening profiles;
- the default dependency-installation network policy;
- the guest-executor or scoped Git-read design required before MVP2;
- user-facing quarantine workflows beyond the minimum operator surface.

## Unresolved questions

None within this decision's scope. The two-round deliberation reached consensus among
Architecture, Integration, Security, and Data Design.

## Verification

An implementation conforms only if automated or reviewable evidence demonstrates all of
the following:

1. The control-plane process can run without a provider daemon socket, provider
   credential, or repository credential in its environment, files, or OS groups.
2. The two brokers run under identities distinct from the control plane and expose only
   authenticated, typed local interfaces.
3. A task sandbox cannot read the mirror, linked-worktree Git administration, sibling
   workspaces, the application database, either broker's filesystem or network IPC
   endpoint, control-plane secrets, or a remote-write Git credential.
4. Path-containment tests cover absolute paths, `..`, symlink swaps, and relevant
   case-folding or Unicode behavior for each supported host filesystem.
5. A stale `(sandbox_uuid, generation)` execution request is rejected and cannot reach a
   replacement sandbox.
6. Provider-contract tests reject caller-selected images, mounts, devices, privileges,
   users, and network modes, and treat unknown capabilities as unsupported.
7. Fetch tests show the broker writes only to the configured bare mirror, uses sanitized
   Git configuration, does not recurse submodules, and does not leak credentials to a
   child, subsequent process, mismatched origin, alternate scheme, or cross-origin
   redirect.
8. Crash tests at every boundary between intent commit, external action, observation,
   and outcome recording converge without duplicate resources or lost intent.
9. A stop-start-stop sequence creates three distinct intents while a retry reuses its
   original `operation_id`.
10. Projection mutation and its transition append are atomic, transition rows carry the
    resulting projection version, and a drift check detects injected inconsistency.
11. Concurrent attempts to transition while a blocking intent appears cannot pass a
    read-then-write race.
12. Reconciliation tests prove that foreign resources and orphan worktrees are never
    deleted automatically, unavailable storage is not treated as absence, observation
    counts survive restart, and elapsed time alone cannot authorize destruction.
13. Two workspaces from the same base commit can execute concurrently without shared
    working-tree state, and fetching the mirror does not mutate either active workspace.
14. A build requiring `.git` metadata produces an explicit unsupported/degraded signal
    on its command or test result—even when the tool exits zero with fallback metadata—
    rather than being reported as a fully representative successful run.
15. Concurrent user and reconciler attempts to allocate a replacement sandbox cannot
    commit the same generation or create two non-terminal bindings for one workspace.

The ADR becomes accepted only when its PR is reviewed by a role other than the
coordinator and merged by the Product Owner under the working agreement.
