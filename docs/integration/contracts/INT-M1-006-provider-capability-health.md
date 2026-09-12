# INT-M1-006 — Provider capability and health discovery

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Provider:** Local Incus
**Requirements:** `FR-M1-006`–`FR-M1-009`

## Purpose

Publish an evidence-backed snapshot of what local Incus can enforce for one instance
kind. Capability discovery is not optimistic feature detection: an unknown or
unevidenced property is `UNSUPPORTED`, and a profile is eligible only when every required
property is `SUPPORTED` for that exact kind.
Discovery runs over the authenticated sandbox-provider broker channel and returns only
safe evidence under the common result and deadline conventions.

## Capability snapshot

```text
CapabilitySnapshot {
  snapshot_id,
  provider_kind: INCUS,
  instance_kind: SYSTEM_CONTAINER | OCI_APPLICATION_CONTAINER | VM,
  incus_daemon_identity,
  adapter_version,
  incus_daemon_version,
  host_capability_fingerprint,
  observed_at,
  expires_at,
  capabilities[] {
    name,
    status: SUPPORTED | UNSUPPORTED | DEGRADED | UNKNOWN,
    evidence_kind,
    safe_evidence,
    limitations[]
  }
}
```

Snapshots are immutable, per instance kind, and expire. A daemon identity/version,
adapter version, or host-capability fingerprint change invalidates the previous snapshot;
broker/appliance startup and host migration force rediscovery. `UNKNOWN` is never coerced
to `SUPPORTED`; `DEGRADED` satisfies a profile only when that exact limitation is
explicitly allowed by trusted policy. A Sandbox binding pins the exact snapshot used for
eligibility.

## MVP1 capability vocabulary

- `atomic-ownership-identity`
- `rootless-or-user-namespace`
- `read-only-mount`
- `masked-path`
- `workspace-path-containment`
- `broker-endpoint-exclusion`
- `network-isolation`
- `network-destination-policy`
- `linux-capability-drop`
- `seccomp-or-equivalent`
- `device-deny-by-default`
- `cpu-limit`, `memory-limit`, `process-limit`
- `guest-exec-argv`
- `exec-working-directory`
- `exec-environment-allowlist`
- `exec-timeout`, `exec-cancellation`, `exec-output-bound`
- `execution-observation-by-operation-id`
- `resource-observation-by-ownership-key`
- `workspace-projection`

New names are additive. A rename is a breaking contract change because profiles persist
names.

## Discovery and eligibility

`discover_capabilities(instance_kind)` actively probes a broker-owned fixture where safe
and otherwise returns versioned, adapter-supplied evidence. Static version claims alone
are insufficient for security properties. `evaluate_profile(profile_name, snapshot_id)`
rejects a snapshot for another instance kind and returns required, missing, degraded, and
satisfied capabilities without creating a resource.

The profile catalogue is server-owned and versioned. A client may select a profile name
but cannot lower its requirements or inject provider configuration.

## Health

`health` distinguishes:

- `HEALTHY`: IPC, daemon, profile catalogue, and required system-container probes succeed;
- `DEGRADED`: Incus remains observable but a required system-container dependency or
  probe is impaired, so new baseline provisioning cannot treat the provider as healthy;
- `UNAVAILABLE`: the provider authority cannot be positively queried.

An unsupported optional OCI/VM kind is not provider degradation. Health and capability
observations are poll-based in MVP1; Incus events can trigger an earlier poll but never
replace it as canonical evidence.
