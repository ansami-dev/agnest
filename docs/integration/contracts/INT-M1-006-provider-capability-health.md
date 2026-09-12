# INT-M1-006 — Provider capability and health discovery

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9
**Providers:** Docker, Incus/LXC, future VM providers
**Requirements:** `FR-M1-006`–`FR-M1-009`

## Purpose

Publish an evidence-backed snapshot of what a provider adapter can enforce. Capability
discovery is not optimistic feature detection: an unknown or unevidenced property is
`UNSUPPORTED`, and a profile is eligible only when every required property is `SUPPORTED`.
Discovery runs over the authenticated sandbox-provider broker channel and returns only
safe evidence under the common result and deadline conventions.

## Capability snapshot

```text
CapabilitySnapshot {
  snapshot_id,
  provider_kind,
  adapter_version,
  provider_version,
  host_fingerprint,
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

Snapshots are immutable and expire. A provider/host/adapter upgrade invalidates the
previous snapshot. `UNKNOWN` is never coerced to `SUPPORTED`; `DEGRADED` satisfies a
profile only when that exact limitation is explicitly allowed by trusted policy.

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
- `resource-observation-by-label`
- `workspace-projection`

New names are additive. A rename is a breaking contract change because profiles persist
names.

## Discovery and eligibility

`discover_capabilities` actively probes a broker-owned fixture where safe and otherwise
returns versioned, adapter-supplied evidence. Static version claims alone are insufficient
for security properties. `evaluate_profile(profile_name, snapshot_id)` returns required,
missing, degraded, and satisfied capabilities without creating a resource.

The profile catalogue is server-owned and versioned. A client may select a profile name
but cannot lower its requirements or inject provider configuration.

## Health

`health` distinguishes:

- `HEALTHY`: IPC, daemon, profile catalogue, and required probes succeed;
- `DEGRADED`: the adapter remains observable but one or more non-required capabilities or
  fixtures fail;
- `UNAVAILABLE`: the provider authority cannot be positively queried.

Health and capability observations are poll-based in MVP1. Provider events can trigger an
earlier poll but never replace it as canonical evidence.
