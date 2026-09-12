# MVP1 architecture sequences

**Status:** Proposed  
**Owner:** Architecture (Codex)  
**Issue:** #7  
**Decision:** `ADR-0003`

These sequences show ownership and durable ordering. Method names and payload shapes are
illustrative; Integration owns the eventual contracts.

## Connect or refresh a Repository

```mermaid
sequenceDiagram
    actor O as Operator
    participant C as Control plane
    participant R as Repository service
    participant D as Metadata store
    participant F as Credentialed-fetch broker
    participant M as Bare mirror
    participant G as Remote Git host

    O->>C: connect or refresh repository
    C->>R: validate intent
    R->>D: commit Fetch intent(operation_id, canonical_origin)
    D-->>R: committed
    R->>F: fetch(repository_id, origin, operation_id)
    F->>F: validate scheme/origin and select credential
    F->>G: authenticated fetch, cross-origin redirects refused
    G-->>F: Git objects and refs
    F->>M: update mirror under repository lock
    F->>M: observe resulting refs
    F-->>R: typed result and evidence
    R->>D: record outcome and fetched refs
    R-->>C: repository fetch state
    C-->>O: confirmed result
```

An active Workspace base never follows the mirror's updated ref. Creating another
Workspace resolves a new base explicitly.

### Ambiguous fetch outcome

```mermaid
sequenceDiagram
    participant R as Repository service
    participant D as Metadata store
    participant F as Fetch broker
    participant M as Bare mirror

    R->>D: commit Fetch intent
    R->>F: fetch(operation_id)
    F->>M: update mirror
    Note over F,R: connection fails before result is delivered
    R->>D: mark intent UNKNOWN_OUTCOME
    R-->>R: schedule reconciliation
    R->>F: observe(operation_id, expected refs)
    F->>M: inspect refs and operation evidence
    alt effect confirmed
        F-->>R: APPLIED with observed refs
    else effect absent
        F-->>R: OBSERVED_ABSENT
        R->>F: retry same operation_id
    else mirror unavailable
        F-->>R: UNOBSERVABLE
    end
```

## Create a Workspace and Sandbox

```mermaid
sequenceDiagram
    actor O as Operator
    participant C as Control plane
    participant D as Metadata store
    participant W as Git workspace service
    participant FS as Workspace filesystem
    participant P as Provider broker
    participant S as Task sandbox

    O->>C: create Workspace(repository, base SHA, profile)
    C->>D: create Workspace UUID and Worktree intent
    D-->>C: committed
    C->>W: create worktree(operation_id, workspace_id, base SHA)
    W->>FS: create linked worktree under Workspace root
    W->>FS: observe path, HEAD, and base SHA
    W-->>C: applied with evidence
    C->>D: record Worktree outcome
    C->>D: atomically allocate generation and create Sandbox intent
    D-->>C: unique non-terminal binding committed
    C->>P: create(workspace_id, generation, profile, operation_id)
    P->>P: resolve server-owned confinement
    P->>S: create with ownership and operation labels
    P->>S: observe identity, generation, and health
    P-->>C: applied with provider reference
    C->>D: record Sandbox outcome and READY projection
    C-->>O: Workspace ready
```

If a concurrent user action and reconciler both request a replacement, the database
constraint admits only one non-terminal binding. The losing transaction creates no
provider resource.

### Crash windows during create

```mermaid
stateDiagram-v2
    [*] --> IntentCommitted
    IntentCommitted --> EffectAbsent: crash before external call
    IntentCommitted --> EffectUnknown: call started; no durable result
    IntentCommitted --> OutcomeRecorded: applied result recorded
    EffectAbsent --> Retried: positive absence observed
    EffectUnknown --> OutcomeRecorded: ownership label confirms effect
    EffectUnknown --> Retried: positive absence observed
    EffectUnknown --> Wait: provider or filesystem UNOBSERVABLE
    Retried --> OutcomeRecorded: same operation converges
    Wait --> EffectUnknown: next reconciliation pass
    OutcomeRecorded --> [*]
```

The state diagram is for an external-operation intent, not `WorkspaceState`.

## Execute a Command or Test

```mermaid
sequenceDiagram
    actor O as Operator
    participant E as Execution gateway
    participant D as Metadata store
    participant P as Provider broker
    participant S as Task sandbox
    participant B as Blob store

    O->>E: run(argv, cwd, timeout, output limit)
    E->>D: read active sandbox UUID, generation, Workspace revision
    E->>E: validate cwd and execution policy
    E->>D: commit Execution intent
    E->>P: exec(sandbox UUID, generation, bounded request)
    P->>P: reject stale generation; revalidate cwd
    P->>S: execute inside existing confinement
    S-->>P: stdout, stderr, exit, timestamps
    P-->>E: bounded result or typed failure
    E->>B: write immutable large output
    E->>D: atomically record outcome, blob refs, revision, conditions
    E-->>O: result with GitMetadataUnavailable when applicable
```

Timeout and cancellation produce explicit outcomes. A connection loss after dispatch is
`UNKNOWN_OUTCOME`; the system does not blindly retarget or replay a possibly mutating
command against a replacement generation.

## Stop, discard, or archive

```mermaid
sequenceDiagram
    actor O as Operator
    participant C as Control plane
    participant D as Metadata store
    participant P as Provider broker
    participant W as Git workspace service

    O->>C: discard Workspace
    C->>D: atomically verify no blocking unresolved intents
    C->>D: commit StopSandbox intent
    C->>P: stop(sandbox UUID, generation, operation_id)
    P-->>C: observed stopped
    C->>D: record stop outcome
    C->>D: commit DestroySandbox intent
    C->>P: destroy(sandbox UUID, generation, operation_id)
    P-->>C: observed absent
    C->>D: record destroy outcome
    C->>D: commit DiscardWorktree intent
    C->>W: discard(workspace_id, operation_id)
    W->>W: verify root availability, ownership, and path containment
    W-->>C: observed absent or quarantined
    C->>D: record final outcome
    C-->>O: discarded or operator action required
```

Archive replaces discard's final deletion with a retained Workspace and immutable
artifact references. A worktree that lacks matching metadata is never deleted by this
flow; reconciliation quarantines it.

## Startup reconciliation

```mermaid
sequenceDiagram
    participant C as Control plane
    participant D as Metadata store
    participant R as Reconciler
    participant W as Git workspace service
    participant P as Provider broker

    C->>R: start reconciliation pass(deployment_id)
    R->>D: load unresolved intents and expected resources
    par observe filesystem
        R->>W: observe expected and owned worktrees
        W-->>R: PRESENT, ABSENT, or UNOBSERVABLE with evidence
    and observe provider
        R->>P: observe resources by deployment/workspace/generation labels
        P-->>R: PRESENT, ABSENT, or UNOBSERVABLE with evidence
    end
    R->>D: persist attributed observations and counts
    loop each discrepancy
        alt safe retry of committed intent
            R->>R: invoke same application port and operation_id
        else owned provider orphan
            R->>R: stop or quarantine
            Note over R,D: destroy only after age and observation thresholds
        else unowned worktree
            R->>W: quarantine; preserve unpublished files
        else foreign or inconclusive
            R->>D: block mutation and request operator resolution
        end
    end
```

The observation count is persisted and may advance across ordinary reconciliation
passes. A restart neither resets it nor counts as evidence by itself.

## Failure ownership summary

| Failure | Immediate owner | Durable result | Recovery owner |
|---|---|---|---|
| Remote authentication or origin rejection | Fetch broker | Typed failed Fetch intent | Repository service/operator |
| Mirror write interrupted | Fetch broker | `UNKNOWN_OUTCOME` plus mirror observation | Reconciler through Repository port |
| Worktree create interrupted | Git workspace service | Intent plus filesystem observation | Reconciler through Workspace port |
| Provider create response lost | Provider broker | Intent plus provider labels/observation | Reconciler through Provider port |
| Sandbox crashes | Provider broker observes; control plane owns lifecycle | Sandbox condition and operation history | Reconciler/operator |
| Command transport lost | Execution gateway | `UNKNOWN_OUTCOME`; no automatic retarget | Operator/reconciler |
| Metadata store unavailable | Control plane | No uncommitted external action may begin | Retry after store health returns |
| Workspace root unavailable | Git workspace service | `UNOBSERVABLE`, never inferred absent | Reconciler after root returns |
