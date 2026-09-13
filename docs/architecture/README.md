# Architecture

Owner: Architecture role (Codex). See `docs/agents/roles.md`.

Contents as each MVP is worked:

- `boundaries-M<n>.md` — components (`ARC-M<n>-<nnn>`): responsibility, interface,
  dependencies, and failure behaviour
- `sequences-M<n>.md` — sequence diagrams for the flows each PRD §18 asks for
- `invariants-M<n>.md` — what must hold across components, stated so a later PR can be
  checked against it
- `verification-M<n>.md` — measurable NFR contracts and the acceptance/requirement
  matrix that separates design evidence from executable release evidence

`ARC-` IDs are allocated in `docs/agents/id-registry.md` before the work starts.
Component names are drawn from `docs/glossary.md` and `docs/data/entity-register.md`;
a name used here that neither file defines is added there in the same PR.

This directory is created by the Security and Data Design roles only so that all four
disciplines have a symmetric, tracked home from the first commit. Its contents are the
Architecture role's to write.
