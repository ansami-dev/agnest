# Architecture Decision Records

A decision that only exists in a conversation is a decision the next person will
re-litigate. ADRs are how Agnest keeps design state durable — the same reason the
product itself keeps engineering state in artifacts rather than transcripts.

## Rules

1. **Numbering.** `ADR-<nnnn>` is the number of the GitHub issue that produced the ADR.
   Allocated once and never reused; a withdrawn number stays withdrawn. Numbers will have
   gaps, which is fine — ADRs are cited by ID, not read in sequence.
2. **Filename.** `ADR-<nnnn>-<kebab-slug>.md`.
3. **Proposed ADRs are editable.** While the PR is open, change anything.
4. **Accepted ADRs are immutable.** Do not edit an accepted ADR to correct, extend, or
   reverse it. Write a new ADR carrying `Supersedes: ADR-<nnnn>`, and update *only the
   status line* of the old one to `Superseded by ADR-<mmmm>`.
5. **One decision per ADR.** If the title needs "and", it is two ADRs.
6. **Disagreement is recorded, not resolved away.** The *Unresolved questions* section
   names the position and the role holding it. The Product Owner decides, and that
   decision is appended as a new ADR, not as an edit.

## Where ADRs come from

Most ADRs are the output of a Deliberation issue (`docs/agents/roles.md` §3.1). The
coordinator named in that issue opens one ADR PR after the deliberation terminates.

A single role may also decide something wholly inside its own scope that the other roles
will nonetheless have to live with. That still opens an issue first — **every ADR has an
originating issue, with no exception and no PR-number fallback.** The issue may be
answered in one comment by one role; what matters is that the number exists, that the
question is on the record, and that the ADR cannot arrive without one.

## Status values

| Status | Meaning |
|---|---|
| `Proposed` | Under discussion. The PR is open. Editable. |
| `Accepted` | Merged and binding. Immutable. |
| `Superseded by ADR-<nnnn>` | Replaced. Kept for the record; never deleted. |
| `Withdrawn` | Never accepted. The number is retired. |

## Index

<!-- Add a row when an ADR is accepted. -->

| ID | Title | Status | Decides for |
|---|---|---|---|
| [ADR-0003](ADR-0003-mvp1-component-authority-boundaries.md) | Enforce three authority boundaries around the MVP1 modular control plane | Accepted | MVP1 |
| [ADR-0011](ADR-0011-local-incus-provider-for-mvp1.md) | Use local Incus as the sole MVP1 sandbox provider | Accepted | MVP1 |
| [ADR-0013](ADR-0013-product-wide-technology-architecture.md) | Govern implementation with an evolvable product-wide technology architecture | Accepted | MVP1–MVP8 |
