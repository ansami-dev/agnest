# Architecture Decision Records

A decision that only exists in a conversation is a decision the next person will
re-litigate. ADRs are how Agnest keeps design state durable — the same reason the
product itself keeps engineering state in artifacts rather than transcripts.

## Rules

1. **Numbering.** `ADR-<nnnn>`, sequential, allocated once and never reused. A withdrawn
   number stays withdrawn.
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

An ADR may also be written directly when a single role makes a decision wholly inside
its own scope that other roles will nonetheless have to live with.

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
| — | — | — | — |
