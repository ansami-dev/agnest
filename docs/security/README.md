# Security

Owner: Security role (Claude). See `docs/agents/roles.md`.

Contents as each MVP is worked:

- `threat-model-M<n>.md` — trust zones, boundaries, and threats (`THR-M<n>-<nnn>`)
- `controls-M<n>.md` — controls (`SEC-M<n>-<nnn>`), each with a testable verification statement
- `conformance/` — minimum security conformance tests per sandbox provider and per adapter

A threat without a control is an open item, and is listed as one. A control without a
verification statement is a preference, not a control.
