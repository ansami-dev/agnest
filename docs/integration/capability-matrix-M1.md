# MVP1 provider capability matrix

**Status:** Proposed baseline; every deployment records an observed snapshot.
**Owner:** Integration (Codex)
**Issue:** #9
**Contract:** `INT-M1-006`

This matrix states expectations for the one MVP1 provider, local Incus. Its columns are
instance kinds, not interchangeable providers. `Required` means that kind must evidence
the capability before its profile is eligible. `Optional kind` means the entire kind may
be unavailable without degrading provider health.

| Capability | System container | OCI application container | Incus VM | MVP1 rule |
|---|---|---|---|---|
| Instance-kind availability | Required baseline | Optional kind | Optional kind; nested virtualization required | Health uses the system-container baseline only |
| Atomic ownership identity at create | Required via config/name | Required via config/name | Required via config/name | Required independently per kind |
| User namespace or stronger isolation | Required | Required if kind enabled | Dedicated kernel boundary | Evidence is kind-specific |
| Read-only and masked mounts | Required | Required if kind enabled | Required equivalent if kind enabled | No fallback to another kind's result |
| Workspace path containment | Required | Required if kind enabled | Required if kind enabled | Broker revalidates the projection |
| Broker socket exclusion | Required | Required if kind enabled | Required if kind enabled | Socket never enters an instance |
| Network isolation/destination policy | Required by profile | Required by profile | Required by profile | Profile eligibility fails closed |
| Linux capability drop | Required | Required if kind enabled | Guest policy, not container capability set | Evidence remains kind-specific |
| Seccomp or equivalent | Required by profile | Required by profile | Guest/hypervisor equivalent | Limitations are explicit |
| Device deny by default | Required | Required if kind enabled | Required if kind enabled | Required independently per kind |
| CPU/memory/process limits | Required | Required if kind enabled | Required if kind enabled | Required independently per kind |
| Typed argv guest execution | Required | Required if kind enabled | Required if kind enabled | Same logical contract, separate proof |
| Working-directory revalidation | Broker-required | Broker-required | Broker-required | Always required |
| Timeout, cancellation, output bound | Required | Required if kind enabled | Required if kind enabled | Same logical contract, separate proof |
| Execution observation by operation ID | Optional capability | Optional capability | Optional capability | Absence forces operator resolution |
| Resource observation by ownership | Required | Required if kind enabled | Required if kind enabled | Required independently per kind |
| Workspace projection with Git admin hidden | Required | Required if kind enabled | Required if kind enabled | Always required for an eligible kind |

Each column produces a separate immutable `CapabilitySnapshot`. A Sandbox binding pins
one snapshot, and expiry or daemon, adapter, or host-capability change forces rediscovery.
No row authorizes inference or fallback across instance kinds.
