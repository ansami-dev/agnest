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
| — | — | — | — | — |

## `NFR-` — Non-functional requirements · owner: first citing role

Allocated when a PRD §8 clause first needs to be cited by ID.

| ID | PRD clause | Issue | Status |
|---|---|---|---|
| — | — | — | — |
