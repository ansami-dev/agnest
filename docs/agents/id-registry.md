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

- `ENT-` and `EVT-` are name-derived, and live in `docs/data/entity-register.md`.
- `ADR-` takes the number of the GitHub issue that produced it, or of its own PR.
  Issues and PRs share one counter per repository, so GitHub allocates it for us.

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
| — | — | — | — |

## `INT-` — Integration contracts · owner: Integration

| ID | Title | Issue | Status |
|---|---|---|---|
| — | — | — | — |

## `NFR-` — Non-functional requirements · owner: first citing role

Allocated when a PRD §8 clause first needs to be cited by ID.

| ID | PRD clause | Issue | Status |
|---|---|---|---|
| — | — | — | — |
