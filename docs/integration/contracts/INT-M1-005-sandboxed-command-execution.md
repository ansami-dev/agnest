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
  standard_input: NONE | bounded_blob_reference,
  timeout_ms,
  output_limit_bytes,
  cancellation_id
}
```

`argv` is never converted to a host-shell string. Shell semantics require an explicit
shell executable in `argv`. Environment values are resolved by the Execution Gateway
from an allowlist and transmitted over authenticated IPC; the request cannot inherit the
control-plane or broker environment. Remote Git write credentials are excluded.

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

## Cancellation

Cancellation targets both `cancellation_id` and the original `operation_id`. An
acknowledgement distinguishes `REQUESTED`, `DELIVERED`, and `PROCESS_EXIT_CONFIRMED`.
Only the last proves the process ended. Timeout uses the same cancellation path and does
not imply successful termination.

## Health

Health verifies Incus guest execution, bounded output transport, cancellation, and
observation retention when advertised, using a broker-owned fixture. The system-container
probe is mandatory; optional OCI/VM probe status is reported per kind and cannot be reused
or degrade overall provider health merely because the kind is unsupported. Health never
executes repository content.
