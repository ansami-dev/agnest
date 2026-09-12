## What this changes

<!-- One paragraph. What exists after this merges that did not before. -->

## Traceability

| | |
|---|---|
| **Closes issue** | # |
| **Requirements served** | `FR-…`, `NFR-…` |
| **Decisions applied** | `ADR-…` (or none) |
| **IDs allocated here** | `THR-M<n>-…`, `SEC-M<n>-…`, `ARC-M<n>-…`, `INT-M<n>-…`, `NFR-M<n>-…` (registry) · `ENT-…`, `EVT-…` (name-derived) · or none |

Commit trailers must already carry these — see `docs/agents/roles.md` §4.

## Role

- [ ] Security (Claude)
- [ ] Data Design (Claude)
- [ ] Architecture (Codex)
- [ ] Integration (Codex)

## Definition of done

<!-- Tick the row for your discipline; delete the others. roles.md §10. -->

- [ ] **Security** — threat has a `THR-` ID, the affected trust boundary is named, the control has a `SEC-` ID, and the verification statement is testable
- [ ] **Data Design** — entity has an `ENT-` ID, identity and uniqueness rules stated, immutable vs mutable fields separated, state machine lists legal transitions, retention noted
- [ ] **Architecture** — component has an `ARC-` ID, boundary and dependencies stated, failure behaviour described
- [ ] **Integration** — contract has an `INT-` ID, auth, error taxonomy, health check, and a conformance test

## Checks

- [ ] New or changed terms are defined in `docs/glossary.md`, and no term is used in a sense that file contradicts
- [ ] New entities are in `docs/data/entity-register.md` and new event types in `docs/data/event-register.md` — events are not filed as entities
- [ ] Any ADR here cites an originating issue; no ADR takes a PR number
- [ ] No accepted ADR was edited; any reversal is a new ADR carrying `Supersedes:`
- [ ] No secret, token, or credential value appears in the diff, in test fixtures, or in example config
- [ ] Cross-document links resolve

## Separation of duties

- [ ] I am not going to approve or merge this PR myself (`roles.md` §7)

**Protected change** — tick any that apply. Any tick requires **human** approval, not agent approval alone:

- [ ] CI workflows or `.github/workflows/**`
- [ ] Secrets, tokens, or credential handling
- [ ] `.gitignore` changes that could newly permit a secret-bearing path
- [ ] `docs/agents/**` or the working agreements themselves

## Open questions

<!-- Disagreement that survived review goes here, with the role that holds it named.
     Never dropped silently. The Product Owner decides. -->
