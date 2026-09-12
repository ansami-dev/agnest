# INT-M1-004 — Sandbox provider lifecycle

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Providers:** Docker, Incus/LXC, future VM providers
**Requirements:** `FR-M1-005`–`FR-M1-010`, `FR-M1-016`, `FR-M1-019`

## Purpose and authority

The sandbox-provider broker turns a trusted profile name into a confined provider
resource. It owns daemon credentials and provider-native configuration. The caller cannot
supply an image, mount, device, privilege, network, runtime user, provider name, or raw
container/VM specification.
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
in the provider create call through labels or a deterministic provider name.

### Create

The broker resolves a versioned profile and capability snapshot. It validates that the
provider proves every required capability, broker endpoints are excluded from mounts and
network routes, the Workspace projection belongs to the request, and no non-terminal
resource with conflicting identity exists. A retry observes by full identity before
creating.

Success returns provider kind, opaque provider resource reference, profile version,
capability snapshot ID, observed state, and ownership evidence. The provider reference is
a locator, never product identity.

### Start and stop

Start and stop reject a stale generation. Stop is idempotent for an already-stopped owned
resource. A deadline or lost response after dispatch may be `UNKNOWN_OUTCOME`; callers
observe before retrying.

### Observe

Observation is side-effect free and returns `OBSERVED_PRESENT`, `OBSERVED_ABSENT`, or
`UNOBSERVABLE`, plus authority, time, provider reference, ownership labels, generation,
runtime state, and health evidence. Absence is valid only when the provider authority was
positively reachable.

### Destroy

Destroy requires a typed evidence bundle proving current ownership, matching generation,
positive provider availability, stopped/quarantined state, minimum age, and the configured
durable count of distinct observations. The broker re-observes immediately before the
effect. Missing/foreign ownership, stale evidence, or an unavailable provider fails
closed. The request cannot ask the broker to relabel or adopt a resource.

## Workspace projection

The profile projects only assigned source and declared ephemeral paths. It hides linked
worktree `.git` administration, the bare mirror, sibling workspaces, control-plane and
blob roots, broker IPC, and daemon endpoints. The broker returns whether Git metadata is
available inside the sandbox; it does not fabricate it.

## Provider mappings

- **Docker:** create-time labels and server-resolved container configuration; daemon/API
  access remains broker-only.
- **Incus/LXC:** create-time config keys or deterministic name and server-resolved
  instance profile; Incus socket remains broker-only.
- **Future VM:** must provide equivalent atomic ownership, peer-authenticated management,
  workspace containment, ownership observation, and stale-generation behavior. A VM
  adapter is not eligible by resemblance alone.

## Health

Health checks authenticated IPC, provider daemon reachability/version, profile catalogue
integrity, ownership-label round-trip support, and the ability to evidence every declared
security capability using non-production fixtures. It never creates a user Workspace.
