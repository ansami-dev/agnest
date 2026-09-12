# MVP1 provider capability matrix

**Status:** Proposed baseline; every deployment records an observed snapshot.
**Owner:** Integration (Codex)
**Issue:** #9
**Contract:** `INT-M1-006`

This matrix states the contract expectation, not a claim that every host configuration
already satisfies it. `Required` means an eligible MVP1 profile must demonstrate the
capability. `Optional` means the adapter declares support and limitations explicitly.

| Capability | Docker | Incus/LXC | Future VM | MVP1 profile rule |
|---|---|---|---|---|
| Atomic ownership identity at create | Required via labels/name | Required via config/name | Required | Required |
| Rootless or user namespace | Host-dependent | Host-dependent | Equivalent isolation | Required or Security-approved equivalent |
| Read-only and masked mounts | Required | Required | Required | Required |
| Workspace path containment | Required | Required | Required | Required |
| Broker endpoint exclusion | Required | Required | Required | Required |
| Network isolation/destination policy | Host-dependent | Host-dependent | Required equivalent | Required by selected profile |
| Linux capability drop | Required | Required | N/A or equivalent | Required where Linux applies |
| Seccomp or equivalent syscall policy | Host-dependent | Host-dependent | Hypervisor/guest equivalent | Required by selected profile |
| Device deny by default | Required | Required | Required equivalent | Required |
| CPU/memory/process limits | Required | Required | Required equivalent | Required |
| Typed argv guest execution | Required | Required | Required | Required |
| Working-directory revalidation | Broker-enforced | Broker-enforced | Broker-enforced | Required |
| Timeout, cancellation, output bound | Required | Required | Required | Required |
| Execution observation by operation ID | Optional adapter retention | Optional adapter retention | Optional | Optional; absence forces operator resolution |
| Resource observation by ownership | Required | Required | Required | Required |
| Workspace projection with Git admin hidden | Required | Required | Required | Required |

An implementation replaces each expectation with an immutable observed
`CapabilitySnapshot`. No row authorizes a fallback to a weaker behavior.
