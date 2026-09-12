# Integration

Owner: Integration role (Codex). See `docs/agents/roles.md`.

Contents as each MVP is worked:

- `contracts/<provider>.md` — contracts (`INT-M<n>-<nnn>`): auth, operations, error
  taxonomy, rate limits, health check, version compatibility. The contract ID is
  MVP-scoped; the provider or harness it targets is metadata recorded in the document and
  in the registry, so the contract keeps its identity when the implementation changes
- `capability-matrix-M<n>.md` — what each provider or harness actually supports, so
  capability differences are declared rather than hidden behind a uniform abstraction
- `conformance/` — conformance tests per adapter

`INT-` IDs are allocated in `docs/agents/id-registry.md` before the work starts.

This directory is created by the Security and Data Design roles only so that all four
disciplines have a symmetric, tracked home from the first commit. Its contents are the
Integration role's to write.
