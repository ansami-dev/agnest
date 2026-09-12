# ADR-0011: Use local Incus as the sole MVP1 sandbox provider

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-09-13 |
| **MVP** | MVP1 |
| **Coordinator** | Architecture (Codex) |
| **Originating issue** | #11 |
| **Supersedes** | none |
| **Amends** | Provider implementation and placement scope in `ADR-0003`; all other decisions remain authoritative |
| **Requirements** | `FR-M1-006`, `FR-M1-007`, `FR-M1-008`, `FR-M1-009`, `FR-M1-019` |

## Context

Agnest MVP1 runs as an appliance inside a Linux virtual machine and needs a sandbox
provider on that same appliance. The earlier product scope named separate Docker and LXC
providers and required a future-VM compatibility surface. During Integration design, a
remote-provider interpretation also exposed an unmade architectural decision: a remote
daemon cannot directly mount the canonical worktree stored in the Agnest VM. Supporting
it safely would require a remote worker, workspace replication and delta import, remote
identity, and additional reconciliation behavior.

The Product Owner removed remote providers from the plan until demonstrated demand and
selected Incus as the local provider. Incus gives one API and profile model for system
containers, OCI application containers, and virtual machines, while still allowing each
instance kind to declare different capabilities.

This decision narrows only provider implementation and placement. `ADR-0003` remains
authoritative for privilege separation, server-owned confinement, canonical state,
intent journaling, observation, and conservative reconciliation.

## Decision

MVP1 implements one sandbox provider: an Incus daemon local to the Agnest appliance VM.
`ARC-M1-005` reaches it through broker-owned local access; the control plane and task
sandboxes never receive the Incus socket or daemon authority.

Only the sandbox-provider broker OS identity may hold `incus-admin` membership or any
equivalent group, ACL, credential, or socket grant that confers Incus daemon authority.
The control-plane and credentialed-fetch broker identities must not hold any such grant.

Incus instance kinds are treated as capability variants, not separate providers:

- **System container** is the required MVP1 baseline and acceptance-test target.
- **OCI application container** may be enabled only when the local Incus capability
  snapshot proves the required image, execution, mount, network, and limit behavior.
- **Virtual machine** may be enabled only when nested virtualization and every required
  execution/confinement capability are positively evidenced. Its absence does not make
  the MVP1 installation unhealthy.

Unknown capabilities remain unsupported. No instance kind inherits another kind's
conformance result.

Capability evidence is recorded separately for each Incus instance kind. An immutable
snapshot identifies the instance kind, Incus daemon identity and version, adapter
version, host-capability fingerprint, and observation time. A Sandbox binding pins the
exact snapshot that authorized its profile; it never resolves through an unversioned
"current snapshot" reference.

A snapshot becomes ineligible after its expiry or after a change to daemon identity or
version, adapter version, or host-capability fingerprint. Broker/appliance startup and
host migration trigger fresh discovery before an optional instance kind can be selected.
Evidence for a system container cannot authorize an OCI application container or VM, and
the reverse also holds.

Provider health is computed from reachability plus capabilities required by the MVP1
system-container baseline. An unavailable optional OCI or VM capability is reported in
its per-kind capability result and does not degrade overall provider health. A request
for such an unavailable kind fails as unsupported without declaring the local Incus
provider unhealthy.

MVP1 does not implement or specify:

- a remote Incus endpoint;
- a Docker adapter, local or remote;
- a Proxmox LXC or QEMU adapter;
- remote provider credentials or network broker transport;
- a remote worker, Workspace replica, snapshot transfer, or delta-import protocol.

The logical sandbox-provider port remains provider-neutral at the product boundary. That
is an extension seam, not a promise that unimplemented providers are compatible. Adding
another local provider or any remote placement begins with a new issue and ADR. A remote
decision must resolve Workspace locality, authenticated transport, provider credential
custody, canonical-state reconciliation, and recovery of unpublished remote changes
before an adapter contract is accepted.

The existing requirement IDs remain stable, but their MVP1 meanings are narrowed:

| Requirement | MVP1 meaning after this decision |
|---|---|
| `FR-M1-006` | Provider-neutral lifecycle and execution port implemented by local Incus. |
| `FR-M1-007` | Provision a local Incus Sandbox from a server-owned profile. |
| `FR-M1-008` | System-container baseline; OCI application container is capability-gated. |
| `FR-M1-009` | Incus VM is capability-gated and optional; other VM providers are deferred. |

## Consequences

### For Architecture

The MVP1 deployment has one appliance-local Incus daemon behind the existing provider
broker. Architecture does not introduce a remote-worker or Workspace-replica boundary.
The broker and canonical Workspace remain co-located, preserving the direct projection
model from `ADR-0003`.

### For Integration

Provider contracts and conformance cases target Incus only. Local Unix-socket transport
is normative. The capability matrix distinguishes Incus system, OCI application, and VM
instances; it contains no speculative Docker, Proxmox, or generic remote claims.

### For Security

The MVP1 threat model covers the local Incus daemon, broker socket, system-container
baseline, and capability-gated OCI/VM variants. Remote TLS/API-token custody and remote
Workspace transfer threats are not MVP1 controls.

### For Data Design

Provider placement need not model remote workers or Workspace replicas in MVP1. Sandbox
bindings still persist provider kind, Incus instance kind, generation, profile version,
an immutable per-kind capability-snapshot reference, and opaque Incus resource reference.
The snapshot schema includes daemon identity/version, adapter version, host-capability
fingerprint, observation/expiry times, evidence status, and invalidation reason. Data
Design owns the exact entity and constraints without weakening those keys.

## Options considered

| Option | Why not |
|---|---|
| Local Docker plus local Incus | Two daemon authorities and conformance surfaces add cost without a current product need; Incus already covers the required local system-container baseline. |
| Remote Incus, Docker, and Proxmox in MVP1 | Remote compute cannot consume the appliance-local canonical Workspace safely without a worker and transfer/reconciliation design. |
| Incus system, OCI, and VM kinds all mandatory | VM depends on nested virtualization and Incus instance kinds do not necessarily expose identical features. Capability-gating is honest and portable. |
| Remove the provider abstraction entirely | It would bake Incus identifiers and configuration into product identity, making a future demand-driven provider unnecessarily invasive. |

## Unresolved questions

None. Provider placement and MVP1 implementation were decided by the Product Owner in
Issue #11. Future demand may originate a new decision; it is not an unresolved MVP1
commitment.

## Verification

- MVP1 dependency manifests and deployment docs install Incus, not Docker or Proxmox.
- The provider broker uses only local Incus access and rejects caller-supplied endpoints.
- Only the provider-broker identity has `incus-admin` or equivalent daemon authority;
  control-plane and fetch-broker identities fail an Incus socket/API access test.
- System-container conformance is mandatory; OCI and VM conformance run independently
  only when their capabilities are advertised.
- Cross-kind evidence reuse is rejected. Daemon, adapter, or host-capability changes and
  snapshot expiry force rediscovery before profile eligibility is evaluated.
- Provider health remains healthy when its required system-container baseline passes and
  an optional OCI/VM kind is unavailable.
- No MVP1 contract contains remote-worker, Workspace-transfer, Docker, or Proxmox
  behavior.
- Product, Architecture, Integration, Security, and Data Design artifacts cite this ADR
  when describing provider scope.
