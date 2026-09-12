# INT-M1-002 — Credentialed repository fetch

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Providers:** Native Git, GitHub, Forgejo
**Requirements:** `FR-M1-002`, `FR-M1-003`, `FR-M1-017`, `FR-M1-018`

## Purpose and authority

The Repository service asks the credentialed-fetch broker to update one configured bare
mirror. The request names product identities and a registered origin; it never carries a
credential, credential helper, arbitrary environment, refspec, Git config, or output path.
Transport authentication, result envelopes, and deadline ceilings are inherited from
[`README.md`](README.md).

## Request

```text
FetchRequest {
  common_context,
  integration_id,
  origin_role: GIT,
  canonical_origin,
  remote_name,
  mirror_id,
  expected_mirror_root,
  fetch_policy_name
}
```

`remote_name`, mirror location, allowed refspecs, and fetch policy are resolved from
broker-owned configuration. `expected_mirror_root` is a consistency assertion against
that configuration, not an instruction to write elsewhere.

## Preconditions

- The authenticated peer is the configured Repository service identity.
- The URL has no user information and exactly matches the integration's origin registered
  for the `GIT` role.
- The resolved mirror path is beneath the broker's configured mirror root after real-path
  resolution.
- The target is a bare mirror owned by the requested `repository_id`.
- The Repository service holds its per-repository mirror-mutation lease.

## Git execution baseline

The broker invokes Git without a shell, from fixed argv, with a minimal environment.
System/global/repository credential helpers and hooks are disabled; `protocol.ext` and
unapproved transports are denied; submodules are not recursively fetched. A credential is
selected by `(integration_id, GIT)`, verified against the registered `GIT` origin, injected
through a broker-private mechanism, and erased after the operation. An `API`-role
credential is never eligible for Git transport, even when its canonical origin happens to
match. Credential material is never written into the remote URL, mirror config, response,
or logs.

Cross-origin redirects are rejected with `ORIGIN_MISMATCH` against the `GIT` role. A new
origin requires a separately registered remote and integration policy.

## Result and recovery

Success returns pre-fetch and post-fetch ref snapshots, default-branch observation,
object-format metadata, duration, and sanitized Git version. It does not claim which
network operation produced a ref beyond this completed call.

Fetch is idempotent for one configured remote/ref policy. After transport loss or broker
restart, a retry reuses `operation_id`, observes mirror availability, and may safely run
the same fetch again. A missing or unavailable mirror root is `UNOBSERVABLE`, not
`NOT_FOUND`. Existing Workspace base SHAs never move.

## Health

Broker health verifies peer-authenticated IPC, reachability of the `(integration_id, GIT)`
credential binding without reading a secret value into the response, mirror-root
accessibility, Git executable version, and a read-only authenticated remote probe against
the registered `GIT` origin. It does not fetch.
