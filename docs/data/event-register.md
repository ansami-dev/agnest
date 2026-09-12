# Event Register

**Status:** Proposed — becomes binding when this PR is merged.
**Owner:** Data Design. Amendments by PR; any role may propose one.
**Rules:** `docs/agents/roles.md` §4.1.

---

## What belongs here, and what does not

This is the authoritative catalogue of **event types** — `EVT-<PascalName>`. Nothing else
allocates an `EVT-` ID.

An **entity** is a thing that exists. An **event** is a thing that happened. The two are
kept in separate registers because their rules genuinely differ:

| | Entity (`ENT-`) | Event (`EVT-`) |
|---|---|---|
| Register | `docs/data/entity-register.md` | this file |
| Mutability | updated in place | immutable once written |
| Shape change | migration | a new payload version, old versions still readable |
| Deletion | subject to retention policy | subject to retention policy, but never edited |
| Identity | the thing | the occurrence |

`ENT-Workspace` is the workspace. `EVT-WorkspaceDiscarded` is the moment one was thrown
away. The distinction is not pedantry: MVP3 requires that workflow state be reconstructed
from events after a restart (`FR-M3-018`), and replay is only sound if nothing ever edits
an event.

If an entry is named for something that occurred at a point in time, it is an event and
belongs here.

## Rules

1. **`EVT-` IDs are name-derived, not sequential.** Two roles picking the same name mean
   the same event; different names give different IDs. Nothing needs reserving.
2. **Name events in the past tense**, after what happened rather than what was requested:
   `EVT-WorkspaceDiscarded`, not `EVT-DiscardWorkspace`. A command is not an event.
3. **Renaming an event type allocates a new ID.** The old row stays, marked superseded, so
   emitted records and the documents citing them remain readable.
4. **Payload versions are recorded per event**, never by renaming the event. `FR-M3-005`
   requires a payload version on every event; this register is where the current version
   is stated.
5. **Every event carries** a globally unique ID, causation and correlation IDs, actor,
   timestamp, and payload version (`FR-M3-005`, MVP3 §9). Those are universal and are not
   repeated per row.

## Status values

`Reserved` · `Active` · `Withdrawn` · `Superseded by EVT-<Name>`

---

## MVP1 — Git Foundation & Sandboxed Workspaces

Event modelling begins in earnest with the MVP3 event bus (`FR-M3-005`). MVP1 emits
lifecycle and audit records whose event types are allocated when the MVP1 data design
lands; the table is intentionally empty rather than speculatively populated.

| ID | Emitted when | Payload v | Issue | Status |
|---|---|---|---|---|
| — | — | — | — | — |

## MVP2 — Agent Runtime Fabric

| ID | Emitted when | Payload v | Issue | Status |
|---|---|---|---|---|
| — | — | — | — | — |

## MVP3 — Multi-Agent Orchestration & Groups

| ID | Emitted when | Payload v | Issue | Status |
|---|---|---|---|---|
| — | — | — | — | — |

## MVP4 — Review, Quality Gates & Controlled Publish

| ID | Emitted when | Payload v | Issue | Status |
|---|---|---|---|---|
| — | — | — | — | — |

## MVP5 — Repository Intelligence

| ID | Emitted when | Payload v | Issue | Status |
|---|---|---|---|---|
| — | — | — | — | — |

## MVP6 — Context Intelligence & Token Economics

| ID | Emitted when | Payload v | Issue | Status |
|---|---|---|---|---|
| — | — | — | — | — |

## MVP7 — Integrations & Inference Fabric

| ID | Emitted when | Payload v | Issue | Status |
|---|---|---|---|---|
| — | — | — | — | — |

## MVP8 — Governance, Enterprise Security & Scale

| ID | Emitted when | Payload v | Issue | Status |
|---|---|---|---|---|
| — | — | — | — | — |
