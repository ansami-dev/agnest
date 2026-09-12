# INT-M1-004 — Sandbox provider lifecycle

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Provider:** Local Incus
**Requirements:** `FR-M1-005`–`FR-M1-010`, `FR-M1-016`, `FR-M1-019`

## Purpose and authority

The sandbox-provider broker turns a trusted profile name into a confined local Incus
instance. It alone holds `incus-admin` or equivalent daemon authority and owns
provider-native configuration. The caller cannot supply an image, mount, device,
privilege, network, runtime user, endpoint, instance name, or raw Incus specification.
It inherits peer authentication, version negotiation, result envelopes, deadlines, and
error normalization from [`README.md`](README.md).

## Lifecycle surface

```text
create(context, profile_name, workspace_projection)
start(context)
stop(context, grace_deadline)
observe(context)
destroy(context, destruction_evidence)
```

All operations target `(deployment_id, workspace_id, sandbox_uuid, generation)`. Create
also carries `operation_id`; ownership and operation identity are materialized atomically
in the Incus create call through config keys or a deterministic instance name.

### Create

The broker resolves a versioned profile to one Incus instance kind and requires a current
capability snapshot for that exact kind. It validates that the snapshot proves every
required capability, broker endpoints are excluded from mounts and network routes, the
Workspace projection belongs to the request, and no non-terminal resource with
conflicting identity exists. A retry observes by full identity before creating.

Success returns provider kind `INCUS`, Incus instance kind, opaque resource reference,
profile version, pinned per-kind capability snapshot ID, observed state, and ownership
evidence. The provider reference is a locator, never product identity.

### Start and stop

Start and stop reject a stale generation. Stop is idempotent for an already-stopped owned
resource. A deadline or lost response after dispatch may be `UNKNOWN_OUTCOME`; callers
observe before retrying.

### Observe

Observation is side-effect free and returns `OBSERVED_PRESENT`, `OBSERVED_ABSENT`, or
`UNOBSERVABLE`, plus authority, time, provider reference, ownership config keys,
generation,
runtime state, and health evidence. Absence is valid only when the provider authority was
positively reachable.

### Destroy

Destroy requires a typed evidence bundle proving current ownership, matching generation,
positive provider availability, stopped/quarantined state, minimum age, and the configured
durable count of distinct observations. The broker re-observes immediately before the
effect. Missing/foreign ownership, stale evidence, or an unavailable provider fails
closed. The request cannot ask the broker to rewrite ownership keys or adopt a resource.

## Workspace projection

The profile projects only assigned source and declared ephemeral paths. It hides linked
worktree `.git` administration, the bare mirror, sibling workspaces, control-plane and
blob roots, broker IPC, and daemon endpoints. The broker returns whether Git metadata is
available inside the sandbox; it does not fabricate it.

## Incus instance-kind mapping

- **System container:** required MVP1 baseline and mandatory conformance target.
- **OCI application container:** optional; eligible only from its own current capability
  snapshot and conformance result.
- **Virtual machine:** optional; eligible only from its own current capability snapshot,
  including nested-virtualization evidence, and conformance result.

Evidence never transfers between kinds. All kinds use create-time Incus config keys or a
deterministic instance name for atomic ownership identity. The Incus socket remains
broker-only and the endpoint is fixed by deployment, not caller input.

## Health

Health checks authenticated IPC, local Incus reachability/version, profile catalogue
integrity, ownership-key round-trip support, and every capability required by the
system-container baseline using non-production fixtures. Missing optional OCI/VM support
is reported per kind without degrading overall provider health. Health never
creates a user Workspace.
