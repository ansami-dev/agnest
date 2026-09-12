# INT-M1-005 — Sandboxed command execution

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Provider:** Local Incus
**Requirements:** `FR-M1-006`, `FR-M1-011`, `FR-M1-012`, `FR-M1-017`

## Purpose

Execute one bounded command inside an existing sandbox confinement without allowing the
caller to redefine that confinement. Commands and tests share this contract; product
metadata distinguishes their run type.
It runs over the authenticated sandbox-provider broker channel defined by
[`README.md`](README.md); a sandbox cannot reach that channel.
Each enabled Incus instance kind must pass this contract independently; one kind's result
is not evidence for another.

## Request

```text
ExecuteRequest {
  common_context,
  run_id,
  run_kind: COMMAND | TEST,
  argv[],
  working_directory,
  environment_names[],
  standard_input: NONE | bounded_input_stream,
  timeout_ms,
  output_limit_bytes
}
```

`argv` is never converted to a host-shell string. Shell semantics require an explicit
shell executable in `argv`. Environment values are resolved by the Execution Gateway
from an allowlist and transmitted over authenticated IPC; the request cannot inherit the
control-plane or broker environment. Remote Git write credentials are excluded.

The public Control API may accept an immutable blob reference as an input source, but
the Execution Gateway resolves and authorizes it before this broker call. The reference
must belong to the request's Workspace or to a dedicated, expiring caller-upload
namespace already bound to that Workspace and authenticated principal. Any mismatch is
`AUTHORIZATION_DENIED` before provider dispatch. The gateway then supplies a bounded byte
stream over authenticated IPC; the broker never receives a blob reference and has no
authority to dereference the blob store.

The caller-upload path does not add a blob-store writer. Caller bytes pass through the
Control API to the scoped Execution adapter, which alone writes the immutable input blob
and binds its reference to the pre-authorized Workspace/principal namespace. The Control
API and caller never receive blob-root or direct write authority. Retention and expiry are
Data Design policy; expiry cannot widen access or move a reference between scopes.

The broker verifies the current lease and exact generation, then resolves and revalidates
the working directory beneath the assigned Workspace projection at execution time. A
stale generation returns `STALE_GENERATION` and is never redirected.

## Streaming and result

Output frames carry stream (`STDOUT` or `STDERR`), monotonically increasing sequence,
byte count, and timestamp. Ordering is guaranteed within each stream, not between
streams. The final result contains start/end timestamps, exit status or signal,
cancellation acknowledgement, timeout state, captured/truncated byte counts, immutable
blob references, Workspace revision, and environment conditions including
`GitMetadataUnavailable`.

Reaching the output bound stops collection according to the trusted profile policy and
sets explicit truncation metadata. It never silently drops output or embeds raw output in
an error message.

## Ambiguity and recovery

Execution is non-idempotent after dispatch. A lost response, deadline, broker restart, or
unconfirmed cancellation becomes `UNKNOWN_OUTCOME`. The gateway blocks further execution
on that generation and never automatically redispatches the same or a different command.

If `execution-observation-by-operation-id` is advertised, the provider retains bounded
execution state sufficient to distinguish `IN_FLIGHT`, `COMPLETED`, and `ABSENT` until the
gateway acknowledges the result. `ABSENT` is meaningful only from a positively available
provider. Without this capability, explicit operator resolution is the only recovery
path. Operator resolution creates a new intent and records acceptance of possible prior
effects.

One `run_id` maps one-to-one to one persisted execution intent and its `operation_id`.
Neither identifier is reused for a new execution. After an operator accepts an ambiguous
prior effect and elects to execute again, the gateway creates both a new `run_id` and a
new execution `operation_id`, and records `supersedes_run_id` pointing to the preserved
ambiguous run. The earlier run remains `UNKNOWN_OUTCOME`; supersession does not rewrite
history or claim that its process stopped.

## Cancellation

Cancellation is a separate external effect and therefore a separate persisted intent:

```text
CancelExecutionRequest {
  common_context,
  target_run_id,
  target_execution_operation_id
}
```

The `operation_id` in this request identifies the cancellation intent, not the execution
intent. The gateway commits that intent before dispatching cancellation and links it to
the target run and execution operation. Retrying the same cancellation intent reuses its
operation ID; a separately requested later cancellation creates a new cancellation
intent, so one run may have many cancellation intents. An acknowledgement distinguishes
`REQUESTED`, `DELIVERED`, and `PROCESS_EXIT_CONFIRMED`, and each transition is durably
recorded. Only the last proves the process ended. Timeout uses the same intent-before-
effect path and does not imply successful termination.

## Health

Health verifies Incus guest execution, bounded output transport, cancellation, and
observation retention when advertised, using a broker-owned fixture. The system-container
probe is mandatory; optional OCI/VM probe status is reported per kind and cannot be reused
or degrade overall provider health merely because the kind is unsupported. Health never
executes repository content.
