# Data Design

Owner: Data Design role (Claude). See `docs/agents/roles.md`.

Contents as each MVP is worked:

- `entities-M<n>.md` — entity definitions (`ENT-<PascalName>`): identity and uniqueness
  rules, immutable vs mutable fields, relationships, retention
- `state-machines-M<n>.md` — legal transitions and the events that cause them
- `events-M<n>.md` — modelling for the event types catalogued in `event-register.md`:
  correlation and causation, payload versioning, idempotency keys
- `erd/` — diagrams

Two registers live here and they are not interchangeable:

- `entity-register.md` — `ENT-` IDs. Things that exist.
- `event-register.md` — `EVT-` IDs. Things that happened.

An entity is migrated and its rows are updated; an event payload is versioned and its
records are immutable. Keeping one catalogue for both would blur the distinction MVP3's
event model depends on.

Entity and event names are drawn from `docs/glossary.md` and these two registers, and
nowhere else. A name used here that none of them defines is added in the same PR.
