# MVP1 integration contract conventions

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Decisions:** `ADR-0003`, `ADR-0011`

These conventions apply to `INT-M1-001` through `INT-M1-006`. They define the stable
product-facing contract. Provider SDK types, CLI output, HTTP payloads, and daemon errors
remain adapter details and must not leak through it.

## Versioning

Every request carries `contract_version` as a major integer. MVP1 is version `1`.
Additive response fields and new capability names are backward compatible. Removing or
reinterpreting a field, error code, operation, or capability requires a new major
version. Unknown response fields are ignored; unknown requested capabilities fail
closed.

## Common request context

| Field | Rule |
|---|---|
| `contract_version` | Required; exactly one supported major version. |
| `operation_id` | Required UUID for external effects; retries of one persisted intent reuse it. Read-only probes may omit it only where the contract says so. |
| `deployment_id` | Required for provider-resource operations; durable across restart and upgrade. |
| `project_id` | Required product UUID where a Project exists. |
| `repository_id` | Required for repository and Workspace operations. |
| `workspace_id` | Required for Workspace and sandbox operations. |
| `sandbox_uuid` | Required for sandbox operations; never replaced by a provider ID. |
| `generation` | Required non-negative integer for sandbox operations; stale generations are rejected, never redirected. |
| `deadline_at` | Required UTC timestamp for external I/O. It is a deadline, not merely a client-side timeout hint. |
| `trace_id` | Required opaque correlation value; it grants no authority. |

The callee validates identity combinations before starting an effect. Supplying an ID
does not prove ownership; authority comes from the authenticated peer plus persisted
policy and provider observation.

## Broker transport and authentication

The credentialed-fetch and sandbox-provider contracts use peer-authenticated local IPC.
MVP1 runs inside the Linux Agnest appliance VM and uses Unix-domain sockets protected by
filesystem permissions and peer credentials.

- The caller identity is bound by transport configuration, never by a request header.
- Broker endpoints are outside sandbox-visible mounts and denied by sandbox networking.
- A broker rejects a peer whose OS identity is not allowlisted.
- Neither broker accepts bearer credentials inside ordinary request fields.
- Request and response logs redact remote URLs containing user information, environment
  values, credential-store diagnostics, and raw command output.

Remote broker placement, network bearer authentication, remote workers, and Workspace
replication are outside MVP1 under `ADR-0011` and require a new demand-driven decision.

## Result envelope

Every call returns exactly one of:

```text
Success {
  contract_version,
  operation_id?,
  observed_at,
  result,
  warnings[]
}

Failure {
  contract_version,
  operation_id?,
  observed_at,
  error {
    code,
    category,
    retry,
    safe_message,
    provider_code?,
    details?
  }
}
```

`safe_message` contains no secret, raw provider body, command output, or uncontrolled
repository content. `provider_code` is allowlisted metadata, not a raw error string.

## Normalized error taxonomy

| Code | Category | Retry guidance |
|---|---|---|
| `INVALID_ARGUMENT` | caller | Correct request; never retry unchanged. |
| `UNSUPPORTED_CONTRACT_VERSION` | compatibility | Negotiate a supported version. |
| `UNSUPPORTED_CAPABILITY` | compatibility | Select another profile/provider or change intent. |
| `AUTHENTICATION_FAILED` | auth | Repair peer or integration identity; never blind retry. |
| `AUTHORIZATION_DENIED` | auth | Change policy/authority; never blind retry. |
| `ORIGIN_MISMATCH` | policy | Correct the origin registered for the operation's origin role; never follow or retry a mismatched redirect. |
| `STALE_GENERATION` | conflict | Refresh state; never retarget automatically. |
| `CONFLICT` | conflict | Re-observe canonical state before a new attempt. |
| `NOT_FOUND` | state | Valid only after the named authority was positively observable. |
| `UNOBSERVABLE` | availability | Preserve ambiguity and retry observation with backoff. |
| `DEADLINE_EXCEEDED` | availability | Outcome may be unknown after dispatch; follow operation-specific recovery. |
| `CANCELLED` | control | Record whether cancellation was acknowledged; do not infer process exit. |
| `RESOURCE_EXHAUSTED` | capacity | Retry with bounded backoff or different eligible provider. |
| `PROVIDER_UNAVAILABLE` | availability | Re-observe; absence is not proven. |
| `INTEGRATION_UNAVAILABLE` | availability | Keep last confirmed metadata and retry with backoff. |
| `POLICY_VIOLATION` | policy | Change trusted policy/profile; never pass through a raw spec. |
| `PATH_ESCAPE` | policy | Reject and audit; never normalize into an allowed path. |
| `OUTPUT_LIMIT_EXCEEDED` | execution | Result is explicit truncation, not silent success/failure. |
| `UNKNOWN_OUTCOME` | ambiguity | Reconcile by the same `operation_id`; never create a new effect blindly. |
| `INTERNAL` | defect | Fail closed and retain correlation; no provider details to caller. |

Adapters may retain a structured diagnostic blob in the control-plane trust zone. The
normalized response never uses string matching to determine category or retry policy.

## Deadlines, cancellation, and retry

- A client sets a finite deadline for every external I/O operation.
- The server refuses work whose deadline has already elapsed.
- Cancellation is its own persisted external-effect intent with its own `operation_id`,
  committed before dispatch and linked to the target operation. Losing the cancellation
  response yields an ambiguous cancellation outcome, not proof that the effect stopped.
- Transport retry is not operation retry. A retry that can cause an effect reuses the
  persisted `operation_id` and follows that contract's observe-before-act rule.
- Exponential backoff is bounded by the persisted deadline and includes jitter.
- Command execution is non-idempotent after dispatch and is never automatically
  redispatched, even to the same sandbox generation.

MVP1 starts with these operator-configurable budgets. Configuration may lower them;
raising a budget requires changing a trusted integration or sandbox profile, never a
per-request override beyond that profile's ceiling.

| Operation class | Default deadline ceiling |
|---|---|
| Local IPC and health probe | 10 seconds |
| Repository-host metadata request | 15 seconds |
| Remote Git connection establishment | 15 seconds |
| Git fetch idle period / total operation | 60 seconds / 30 minutes |
| Local Git status or diff / mutation or worktree creation | 30 seconds / 2 minutes |
| Provider observe / create, start, stop, or destroy | 10 seconds / 2 minutes |
| Command or test | 15 minutes, capped by the selected profile |

The fetch idle budget resets only on verified protocol progress, not arbitrary stderr
output. A caller may request a shorter command deadline. Deadline expiry after dispatch
still follows the operation's ambiguity rule.

## Health model

Every adapter exposes a side-effect-free health result:

```text
Health {
  status: HEALTHY | DEGRADED | UNAVAILABLE,
  checked_at,
  latency_ms,
  adapter_version,
  provider_version?,
  contract_versions[],
  capability_snapshot_id?,
  safe_diagnostics[]
}
```

`HEALTHY` means the operation's required authority was actually probed, not merely that a
process is running. Health never creates, mutates, fetches, or destroys a resource.

## Push and poll classification

MVP1 contracts are request/response and observation driven. GitHub and Forgejo metadata
and fetch are pull operations; provider lifecycle and execution are commands followed by
observation. No webhook or provider event is authoritative in MVP1. An adapter may use
events as a wake-up hint, but convergence still polls the authoritative Git filesystem
or provider API.
