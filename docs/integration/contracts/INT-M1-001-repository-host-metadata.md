# INT-M1-001 — Repository host metadata

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Providers:** GitHub, Forgejo
**Requirements:** `FR-M1-002`, `FR-M1-004`, `FR-M1-018`

## Purpose

Resolve a registered GitHub or Forgejo remote into normalized repository metadata without
granting the control plane a reusable Git credential. This is a pull-only contract;
webhooks and remote writes are outside MVP1.

For a private repository, the Repository service invokes this contract across the same
peer-authenticated IPC boundary as `INT-M1-002`; the credentialed-fetch broker (or a
broker-private adapter under its OS identity) performs the provider API call. The control
plane never receives the credential. Public anonymous metadata may use the same contract
without credential selection.

## Registration input

| Field | Rule |
|---|---|
| `integration_id` | Opaque reference to platform-controlled integration configuration. |
| `remote_url` | HTTPS URL by default; SSH is allowed only as an explicitly configured scheme. User information is forbidden. |
| `origins[]` | Non-empty set of role-bound origins. Each entry contains `origin_role: API | GIT` and one canonical `(scheme, lowercase host, effective port)`. Each role appears exactly once. |
| `repository_locator` | Provider-native owner/path or namespace/path, retained as metadata rather than authority. |

Canonicalization removes a default port but does not rewrite scheme, host aliases, path,
or repository identity. GitHub.com normally registers `API = https://api.github.com` and
`GIT = https://github.com`; a self-hosted provider may use the same canonical origin for
both roles, but the roles and their credential bindings remain distinct. A redirect or
outbound request that does not match the origin registered for that operation's role
fails with `ORIGIN_MISMATCH`.

## Operations

### `inspect_repository`

Returns normalized host kind, provider repository ID where available, canonical clone
URL, default branch name, visibility, archived/read-only flags, and an observation time.
It must not enumerate secrets or return an authenticated URL.

### `resolve_default_branch`

Returns the current default-branch symbolic name and its observed commit SHA. The value
is a remote observation and does not move any existing Workspace base.

## Authentication

The adapter references `integration_id`; credential material remains inside the
credentialed integration boundary. Fine-grained installation or repository-scoped tokens
are preferred. The minimum grant is metadata read plus contents read. Push, administration,
workflow, organization, and repository-deletion authority are not part of this contract.
The caller is authenticated as described in the shared contract conventions; request
fields cannot select a different principal.

Credential selection is keyed by `(integration_id, origin_role)`. Repository API calls
use only the `API` binding. A Git transport operation such as authenticated `ls-remote`
is delegated through `INT-M1-002` and uses only the `GIT` binding. A credential obtained
for either role is never presented to the other role, even when both roles have the same
canonical origin.

## Provider mapping

| Normalized fact | GitHub | Forgejo |
|---|---|---|
| Stable provider repository ID | Repository/node ID | Repository numeric ID |
| Default branch | Repository metadata API | Repository metadata API |
| Head commit | Git ref/commit API or authenticated `ls-remote` | Git ref/commit API or authenticated `ls-remote` |
| Health | Authenticated metadata read against the registered repository | Authenticated metadata read against the registered repository |

HTTP `429`, provider rate-limit exhaustion, and secondary throttling normalize to
`RESOURCE_EXHAUSTED` with a bounded `retry_after` when supplied. `401` maps to
`AUTHENTICATION_FAILED`; `403` maps to `AUTHORIZATION_DENIED` unless provider metadata
proves throttling; `404` is `NOT_FOUND` only when the provider was reachable and the
authenticated principal may distinguish absence.

## Health and compatibility

Health performs finite, authenticated, read-only probes for every configured origin role:
repository metadata for `API`, and a non-mutating remote reference observation for `GIT`.
The `GIT`-role probe is delegated to the credentialed-fetch broker under `INT-M1-002`;
the `INT-M1-001` API adapter cannot obtain or hold the `GIT` credential binding. Failure
is reported per role. A general provider status page is diagnostic only. The adapter
records the provider API version when exposed and must tolerate additive response fields.
