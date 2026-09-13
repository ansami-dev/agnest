# ID Registry

**Status:** Proposed — becomes binding when the bootstrap PR is merged.
**Purpose:** collision-safe allocation of the sequential identifier families.
**Rules:** `docs/agents/roles.md` §4.1.

---

## How to allocate

1. Append your rows to the table for your prefix — ID, title, owning issue, status.
2. Push that as the **first** commit on your branch, before doing the work.
3. If someone allocated the same number meanwhile, Git raises a conflict on this file.
   The conflict is the detector. Resolve it by renumbering **yours**.

This file is append-only. A withdrawn ID keeps its row with status `Withdrawn`; the
number is never handed to anything else.

Two families are **not** allocated here, because they cannot collide:

- `ENT-` is name-derived and lives in `docs/data/entity-register.md`.
- `EVT-` is name-derived and lives in `docs/data/event-register.md`. Separate from the
  entity register: an entity is a thing that exists, an event is a thing that happened.
- `ADR-` takes the number of the GitHub issue that produced it. Every ADR has an
  originating issue — including single-role decisions — so there is no fallback and
  nothing to reserve.

Status values: `Reserved` (allocated, work in progress) · `Active` · `Withdrawn` ·
`Superseded by <ID>`.

---

## `THR-` — Threats · owner: Security

| ID | Title | Issue | Status |
|---|---|---|---|
| — | — | — | — |

## `SEC-` — Security controls · owner: Security

| ID | Title | Issue | Status |
|---|---|---|---|
| — | — | — | — |

## `ARC-` — Architecture components · owner: Architecture

| ID | Title | Issue | Status |
|---|---|---|---|
| `ARC-M1-001` | MVP1 modular control plane | #3 | Active |
| `ARC-M1-002` | Repository service | #3 | Active |
| `ARC-M1-003` | Git workspace service | #3 | Active |
| `ARC-M1-004` | Credentialed-fetch broker | #3 | Active |
| `ARC-M1-005` | Sandbox-provider broker | #3 | Active |
| `ARC-M1-006` | Execution gateway | #3 | Active |
| `ARC-M1-007` | Recovery reconciler | #3 | Active |
| `ARC-M1-008` | Task sandbox boundary | #3 | Active |

## `INT-` — Integration contracts · owner: Integration

MVP-scoped, not provider-scoped. The provider or harness a contract currently targets is
metadata on the contract, recorded in the Provider column and in the contract document —
never in the ID. A contract keeps its identity when its implementation is swapped,
renamed, or extended to a second provider.

| ID | Title | Provider(s) | Issue | Status |
|---|---|---|---|---|
| `INT-M1-001` | Repository host metadata | GitHub, Forgejo | #9 | Active |
| `INT-M1-002` | Credentialed repository fetch | Native Git, GitHub, Forgejo | #9 | Active |
| `INT-M1-003` | Git workspace operations | Native Git | #9 | Active |
| `INT-M1-004` | Sandbox provider lifecycle | Local Incus | #9 | Active |
| `INT-M1-005` | Sandboxed command execution | Local Incus | #9 | Active |
| `INT-M1-006` | Provider capability and health discovery | Local Incus | #9 | Active |

## `NFR-` — Non-functional requirements · owner: first citing role

Allocated when a PRD §8 clause or a derived architectural constraint first needs to be
cited by ID.

| ID | Requirement | Issue | Status |
|---|---|---|---|
| `NFR-M1-001` | Warm-mirror workspace creation latency | #18 | Active |
| `NFR-M1-002` | Idempotent Git transitions or recoverable conflicts | #18 | Active |
| `NFR-M1-003` | Restart-safe workspace operations and canonical Git state | #18 | Active |
| `NFR-M1-004` | Configurable sandbox resource limits | #18 | Active |
| `NFR-M1-005` | Path normalization and traversal protection | #18 | Active |
| `NFR-M1-006` | Memory-bounded operation on large repositories | #18 | Active |
| `NFR-M1-007` | Explicit intent and audit for destructive Git operations | #18 | Active |
| `NFR-M1-008` | Appliance storage availability under untrusted execution | #18 | Reserved |
