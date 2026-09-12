# Data Design

Owner: Data Design role (Claude). See `docs/agents/roles.md`.

Contents as each MVP is worked:

- `entities-M<n>.md` — entity definitions (`ENT-<PascalName>`): identity and uniqueness
  rules, immutable vs mutable fields, relationships, retention
- `state-machines-M<n>.md` — legal transitions and the events that cause them
- `events-M<n>.md` — event types (`EVT-<PascalName>`), correlation and causation, payload
  versioning, idempotency keys
- `erd/` — diagrams

Entity names are drawn from `docs/glossary.md` and nowhere else. A name used here that
the glossary does not define is added to the glossary in the same PR.
