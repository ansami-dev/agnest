# ADR-0013: Govern implementation with an evolvable product-wide technology architecture

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-13 |
| **MVP** | M0 — cross-cutting foundation for MVP1–MVP8 |
| **Coordinator** | Architecture (Codex) |
| **Originating issue** | #13 |
| **Supersedes** | none |
| **Requirements** | `FR-M1-001`–`FR-M1-020`, `FR-M2-001`–`FR-M2-019`, `FR-M3-001`–`FR-M3-021`, `FR-M4-001`–`FR-M4-022`, `FR-M5-001`–`FR-M5-020`, `FR-M6-001`–`FR-M6-022`, `FR-M7-001`–`FR-M7-021`, `FR-M8-001`–`FR-M8-025` |

## Context

Agnest begins as a solo-friendly Linux appliance but its roadmap adds heterogeneous
agent runtimes, durable orchestration, governed publication, repository intelligence,
context lineage, integrations and inference, plugins, multi-tenancy, high availability,
and distributed workers. Choosing only for MVP1 would make those known transitions
expensive. Deploying an MVP8 platform before demand would make MVP1 expensive instead.

The decision therefore needs more than a list of preferred tools. It must state which
semantics cannot change, which technologies are product-wide defaults with exit seams,
which concrete choices remain for an implementation baseline, and what observable event
justifies each increase in operational complexity.

Two accepted decisions already constrain the answer:

- `ADR-0003` fixes a modular control plane with separate credentialed-fetch and
  sandbox-provider process authorities, persisted intent, conservative reconciliation,
  and Git/workspace ownership rules.
- `ADR-0011` fixes a local Incus daemon as the sole MVP1 sandbox provider. Remote
  providers and workers remain demand-driven.

Issue #13 ran three rounds across Architecture, Integration, Security, and Data Design.
The four-round budget terminated early by consensus. The Product Owner confirmed that
Agnest 1.0 targets personal use rather than high-assurance enterprise operation: it makes
no tamper-evident audit claim and does not commit to customer-managed encryption keys.

## Decision

### 1. Use three decision levels

Every implementation-baseline ADR classifies a choice as one of:

1. **Stable product invariant** — identity, ownership, authority, durability, and
   compatibility semantics. An implementation must comply.
2. **Product-wide default direction** — the preferred technology family. It remains the
   default across MVPs but is replaceable through the port, compatibility path, and
   migration trigger recorded here. It is not product identity.
3. **MVP baseline choice** — exact versions, frameworks, packages, drivers, generators,
   build tools, images, and deployment settings selected for that MVP.

“Replaceable” does not mean “defer every choice.” Language, database, and public contract
changes compound across releases even when data identity survives them. Conversely, a
default direction does not permit its types or names to leak into domain identity.

### 2. Build a contract-first modular monolith with separate authorities

The control plane is a modular monolith. Domain modules communicate in-process through
owned interfaces and do not depend on transport, provider, or persistence
implementations. A module crosses a process or host boundary only for authority
separation, failure isolation, independent scaling, or independent upgrade evidence.

The credentialed-fetch and sandbox-provider brokers remain separate processes and OS
identities per `ADR-0003`. Each privileged binary has:

- an independently enumerable dependency graph and SBOM;
- forbidden-import checks preventing the control-plane HTTP, UI, ORM, forge, inference,
  and template stacks from entering the broker;
- a narrow shared-package budget limited to reviewed identifiers, bounded envelopes and
  errors, contract schemas, and telemetry propagation;
- an independent systemd unit, restart path, and compatible patch/upgrade path.

The product-wide backend language direction is **Go** for the control plane, brokers,
workers, and first-party integrations. A common language does not imply a shared
dependency surface. A different language requires measured library, performance,
independent-release, or security evidence and must preserve the existing wire contract.

### 3. Use distinct contract families under one compatibility policy

One compatibility governance policy applies everywhere: explicit ownership, no silent
reinterpretation, additive-first evolution, declared overlap/deprecation, conformance
evidence, and a recorded migration. Each contract family keeps the mechanics appropriate
to its medium:

| Boundary | Product-wide direction | Compatibility rule |
|---|---|---|
| Public API | REST/JSON described by OpenAPI; resumable SSE for one-way activity; WebSocket only for genuinely bidirectional sessions | Additive changes by default. Semantic breaks use a new public major with a documented overlap. |
| Privileged broker and future worker RPC | Protobuf/gRPC over local Unix-domain sockets; mTLS and workload/node authorization when remote | Preserve and reserve field numbers/names; negotiate protocol and capability ranges; reject no-overlap before effects. |
| Durable events | Agnest-native persisted envelope and event catalogue | Historical payload meaning is immutable. Incompatible meaning uses a new event data schema version or type. |
| Capabilities | Persisted provider-neutral names | Names are never renamed in place. Aliases and deprecation map old names to replacements. |
| Database | Ordered versioned migrations | Expand, migrate/backfill, switch, then contract after the supported mixed-version window. |
| Plugins | Typed serializable handshake and capability contract | Negotiate protocol overlap; unsupported capabilities fail closed. |

A2A and MCP terminate at policy-enforcing adapters. Their types, identifiers, sessions,
and version cadence do not become internal domain contracts. Provider, forge, harness,
inference, and storage integrations use anti-corruption adapters with normalized errors,
timeouts, cancellation, health, retry safety, idempotency, and conformance tests.

The installed Git executable is initially authoritative for Git mutations and documented
machine-readable output. The Incus adapter uses the local API and capability discovery
rather than parsing human CLI output. Exact libraries and supported versions belong to
the relevant baseline.

### 4. Persist Agnest-native events and map them to CloudEvents

The persisted event envelope is owned by Agnest. Its common fields map losslessly to
CloudEvents 1.0 where semantics match, without making a CloudEvents SDK, binding, or
extension convention part of persistence identity.

CloudEvents export/import defines lower-case alphanumeric extension mappings for Agnest
fields not standardized by CloudEvents, including correlation, causation, aggregate
sequence, and tenant scope. Tenant claims on imported events are untrusted; the receiving
integration binding assigns ownership. A transport that does not preserve aggregate
ordering may inform a projection but cannot serve as an authoritative replay source.

### 5. Use PostgreSQL for canonical metadata and Git for source

Git remains canonical for source state. **PostgreSQL** is the product-wide default
relational authority for Agnest identity, lifecycle, intent, correlation, event,
transition, audit, projection checkpoints, and policy references because the roadmap
requires:

- ACID transactions and transactional guards;
- concurrent interactive and reconciliation writers;
- transactional DDL, check constraints, and partial unique indexes;
- indexed structured columns;
- a credible replication and HA path.

The exact PostgreSQL version, driver, query/migration tooling, and appliance packaging
are baseline choices. Application repositories and migration tests isolate engine
details. Vertical scaling and query/index work precede replicas, partitioning, or
sharding.

Audit and workflow transitions are separate logical append-only streams with different
schemas, access rules, and retention. They are written atomically when one operation
produces both. Workflow replay never depends on audit retention, and audit interpretation
never depends on workflow compaction.

### 6. Make ownership explicit from the first schema

Every tenant-owned primary record, message, event, audit entry, blob descriptor,
projection/index document, cache key, and external reference carries tenant scope.
Tenant context is derived from authenticated identity, policy, and the integration
binding, then propagated across RPC and events. Caller payloads, imported envelope
claims, repository paths, Incus names, and filesystem locators never establish it.

Deployment-global records are explicit rather than represented by an absent tenant. A
physical schema uses an ownership discriminator equivalent to `TENANT | GLOBAL`, with a
tenant identifier required exactly for `TENANT`; it does not put a `GLOBAL` sentinel into
a tenant UUID. Even while MVP1 has one tenant, this rule applies to all tenant-owned data
and derived keys from the first MVP1 schema onward, without exception or grandfathered
core records.

### 7. Content-address immutable blobs behind a storage port

Immutable payloads use a content reference containing the hash algorithm/version and
digest. The MVP1 direction is an appliance-local filesystem blob store. Backend path,
layout, replication, and encryption are replaceable and never become artifact identity.
Metadata references are canonical; an unreferenced blob alone is not a product entity.

Every encryptable blob/reference class carries a versioned encryption descriptor. Its
scheme is explicit (`none` initially) rather than absent; later forms may carry opaque
key scope/reference and encrypted data-key metadata. This preserves an encryption/BYOK
path without committing Agnest 1.0 to a KMS, customer-managed keys, or field encryption.

Object storage is introduced when a second control-plane node, distributed workers,
capacity, durability, or recovery objectives make local paths insufficient. Migration
uses dual-write, verified backfill, checksum comparison, read fallback, then cutover.

### 8. Start durable work in the relational authority

Every external effect is driven by persisted intent. Relational leases, append-only
transitions, idempotency, conservative reconciliation, and a transactional outbox form
the starting execution system. The outbox remains the durable dispatch record if a
message broker is later added.

An external workflow engine or event broker creates a new trust and authority zone. It
requires a later ADR and measured evidence: sustained outbox age/dispatch latency,
cross-host delivery, fan-out, timer volume, lease contention, or scheduling fairness that
cannot meet an adopted SLO. Existing envelopes and consumer checkpoints make broker
adoption additive; workflow types migrate individually and old histories remain
readable.

### 9. Keep intelligence stores derived and replaceable

Search, lexical, graph, vector, summary, and cache stores are versioned rebuildable
projections, never authorities over Git or relational metadata. Each derived document or
key carries repository identity, commit or workspace revision, index generation,
ownership scope, and provenance sufficient to rebuild and verify it.

MVP5 selects engines using representative repositories and retrieval SLOs. A replacement
builds beside the current projection, compares results and lineage, switches reads, and
only then retires the old projection.

### 10. Design extensions for process isolation

First-party adapters may run in the control-plane process while trusted and released
together, but their interfaces are typed, serializable, free of shared mutable objects,
and do not call back into internal state. Third-party or user-supplied code always runs
out-of-process under its own identity and declared capabilities.

The plugin host supplies only scoped, short-lived access with deadlines, cancellation,
quotas, health, audit identity, and explicit network/filesystem/tool policy. Plugins never
inherit database access, Incus authority, Git credentials, model credentials, or the
control plane's ambient filesystem or blob-store access. A plugin receives blob content
only through a scoped reference that the host resolves and authorizes for the current
actor, tenant, task, and operation; the plugin cannot dereference arbitrary content
references itself.

Moving an adapter out-of-process is triggered by third-party code, an independent release
cadence, a justified second language, material dependency conflict, privilege separation,
or crash/resource isolation. It reuses the serializable contract and conformance suite;
the product does not depend on an in-process Go plugin ABI.

### 11. Use a browser client generated from the public contract

The product-wide client direction is a browser-first TypeScript application. Its
transport client is generated from OpenAPI and wrapped by handwritten application code;
generated DTOs do not enter domain modules and the UI does not reproduce authorization
or lifecycle decisions.

MVP1 may serve static assets from the appliance. CLI and future native clients reuse the
same public contract. Frontend framework, state library, generator, and build tool are
baseline choices. Separate hosting is triggered only by independent release, CDN, scale,
or tenant-isolation needs.

### 12. Evolve the appliance without assuming co-location

MVP1 is one managed Linux appliance VM with systemd-managed control plane, fetch broker,
Incus broker, PostgreSQL, and static client. Windows is a supported development host, not
the production runtime contract. Nothing assumes co-location except the explicit
workspace/provider locality fixed by `ADR-0003` and `ADR-0011`; mutable cross-component
state uses declared contracts rather than process globals or undeclared filesystem paths.

When availability or placement requires distribution, the topology becomes stateless
control-plane replicas, HA PostgreSQL, shared object storage, and registered workers.
Provider brokers stay node-local beside the resources they control. The control plane
never stretches a privileged local daemon socket across the network; it authenticates a
node agent/broker with mTLS, authorization, leases, and compatibility negotiation.

The initial remote compatibility target is control plane release N with worker/broker N
and N-1 during an upgrade. It becomes a test obligation when remote workers enter scope,
not for MVP1 local IPC.

### 13. Treat upgrade as one durable operation, not one atomic event

An upgrade has one recorded plan, state, and outcome. Its steps are ordered, idempotent,
observable, and independently retryable:

1. preflight and backup;
2. expand-compatible schema;
3. deploy binaries that negotiate old and new contracts;
4. invalidate only capability snapshots whose defining inputs changed;
5. backfill or migrate;
6. switch behavior;
7. contract old schema after the compatibility window closes.

MVP1 may execute these steps as one appliance action. Later rolling upgrades do not
require schema, process, and capability changes to happen simultaneously. A partial
upgrade is a visible recoverable state, not an inference from unrelated logs.

### 14. Make audit claims no stronger than their verifier

Agnest 1.0 makes no tamper-evidence claim and creates no hash chain. Audit provides
durable ordered evidence and supports detection or diagnosis of application-level
consistency defects, partial or failed writes, and restore validation failures. It does
not claim to detect deletion or rollback to a self-consistent prior snapshot. Anyone with
database write authority, including the appliance owner, is outside that assurance.

Audit records have immutable identity, ownership scope, a strictly increasing
per-deployment sequence with gaps permitted, actor, action, target, outcome,
policy/approval evidence, timestamp,
correlation/causation, schema version, and deterministic versioned canonical
serialization. When a protected action requires audit, an append failure means the action
is not recorded as complete. If an external effect may already have occurred, its intent
enters the unknown-outcome path for observation and reconciliation; the system never
pretends the effect was prevented or rolls it back without evidence.

Any future cryptographic commitment must identify its threat actor, verifier, trusted
checkpoint or external anchor, canonical encoding, algorithm agility, chain scope,
concurrent append behavior, retention/deletion semantics, backup/restore, export
verification, and blocking policy. Its assurance begins at the first trusted checkpoint
and is never described as retroactive.

### 15. Standardize observation, testing, packaging, and supply-chain evidence

Application processes propagate request, intent, task, workspace, sandbox generation,
tenant, and integration correlation through structured logs, traces, and metrics using
OpenTelemetry-compatible conventions. Exporters and backends remain replaceable and an
OpenTelemetry Collector is not mandatory in MVP1. Audit is never routed only through
lossy telemetry. Secrets are structurally redacted before diagnostic sinks.

Every applicable release gate includes:

- domain unit and PostgreSQL integration tests;
- API/RPC/event compatibility checks and generated-client clean-diff checks;
- adapter/provider contract fixtures and live conformance smoke tests;
- authentication, authorization, malformed-input, timeout, cancellation, retry,
  idempotency, unknown-outcome, and failure-injection cases;
- migration rehearsal from every supported release and backup/restore tests;
- architecture dependency/forbidden-import tests;
- pinned inputs, license review, per-binary SBOM, provenance/signing, vulnerability
  response, preflight, and recovery instructions.

Exact release tooling, packaging format, telemetry SDK/exporter, and support matrix are
baseline decisions. Novel dependencies require a measurable advantage and an exit path.

### 16. Defer harness credential custody to its owning work

Model-provider credentials are distinct from remote Git write credentials. Where a
harness process runs determines whether such a credential crosses into a boundary that
also executes repository content. The MVP2 threat model and runtime-adapter design decide
custody and injection; MVP7 extends it across inference providers.

Credential injection is a declared harness capability—helper, ephemeral memory,
environment, file, or keyring—not hidden behind a falsely uniform adapter. Unknown is
treated as the weakest durable-file class. This ADR establishes the question and the
capability seam; it does not select a credential mechanism.

## Evolution matrix

| Roadmap stage | Architecture introduced without pre-deploying later infrastructure |
|---|---|
| MVP1 | Linux appliance, modular Go control plane, separate minimal brokers, local Incus, PostgreSQL metadata, local content-addressed blobs, OpenAPI edge, typed local RPC, explicit ownership, durable intent/reconciliation/outbox. |
| MVP2 | Serializable harness adapters and declared credential-injection/capability contracts; no domain dependence on a harness or model. |
| MVP3 | Durable task/group/workflow events and projections on relational transitions/outbox; external workflow engine remains trigger-driven. |
| MVP4 | Forge/CI publication adapters and protected-action audit through the same authority, idempotency, and external-reference rules. |
| MVP5 | Benchmark-selected rebuildable lexical/graph/vector projections with lineage and tenant scope. |
| MVP6 | Context packs and A2A/MCP gateways reuse stable artifact, event, capability, provenance, and policy contracts. |
| MVP7 | Provider/inference/plugin ecosystem uses out-of-process isolation for untrusted code and contract conformance/version negotiation. |
| MVP8 | Stateless control-plane replicas, HA metadata, shared blobs, tenant enforcement, and remote workers are added by moving existing explicit contracts across hosts. |

## Migration triggers

| Change | Observable trigger | Compatibility path |
|---|---|---|
| Another backend language | Independent trust/release boundary or measured library/performance/security advantage | Implement the existing RPC/event contract; run cross-language conformance before cutover. |
| PostgreSQL HA/read scaling | Adopted recovery/availability SLO or measured read/load pressure | Replication/failover with unchanged domain repositories; rehearse promotion and restore. |
| Partitioning/sharding | Retention or tenant/write measurements exceed indexed single-cluster SLO after tuning | Partition hot history first; introduce routing only with tenant-safe dual-write/backfill evidence. |
| Object storage | Shared readers, HA/distributed workers, disk capacity, durability, or recovery objective | Dual-write, checksummed backfill, read fallback, cutover. |
| Message broker/workflow engine | Sustained dispatch lag, fan-out, timers, lease contention, fairness, or cross-host delivery misses an SLO | Relay the durable outbox; migrate consumers/workflow types incrementally with idempotent checkpoints. |
| Out-of-process adapter/plugin | Third-party trust, independent release/polyglot need, dependency conflict, privilege, or crash/resource isolation | Reuse serializable capability contract and conformance suite; shadow safe reads before routing effects. |
| Remote workers | Demonstrated placement/capacity/policy need outside the appliance | Node-local broker, authenticated registration, mTLS, leases, N/N-1 negotiation, artifact transfer, and a new ADR. |
| Specialized search/graph/vector engine | Representative MVP5 benchmark misses retrieval or scale SLO | Parallel projection build, lineage/result comparison, read switch, retire old index. |
| New public/stream transport | Existing HTTP/SSE/WebSocket binding cannot meet a measured consumer interaction or scale requirement | Add a binding/version around unchanged domain semantics and maintain the declared overlap. |
| Cryptographic audit commitment | A real verifier, adversary, compliance claim, or customer requirement exists | New ADR; begin at a trusted checkpoint and do not claim earlier history. |

## Standards and implementation references

These references justify contract and evolution mechanics; they do not transfer product
identity or policy ownership to an external standard:

- [OpenAPI Specification 3.2](https://spec.openapis.org/oas/v3.2.0.html) — language-neutral
  HTTP contract, documentation, generation, and testing.
- [Protocol Buffers proto3 guide](https://protobuf.dev/programming-guides/proto3/) and
  [gRPC authentication](https://grpc.io/docs/guides/auth/) — field compatibility plus
  TLS/mutual-authentication support for later remote RPC.
- [CloudEvents 1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)
  — common event attributes and extension naming constraints used by the edge mapping.
- [A2A specification](https://a2a-protocol.org/latest/specification/) and
  [MCP specification](https://modelcontextprotocol.io/specification/2026-07-28)
  — interoperability remains behind host/policy-controlled adapters.
- [Incus REST API](https://linuxcontainers.org/incus/docs/main/rest-api/) and
  [Git porcelain status](https://git-scm.com/docs/git-status) — supported machine-facing
  provider and Git integration surfaces.
- [OpenTelemetry overview](https://opentelemetry.io/docs/what-is-opentelemetry/) —
  vendor-neutral traces, metrics, and logs with replaceable exporters/backends.
- PostgreSQL documentation for
  [constraints](https://www.postgresql.org/docs/current/ddl-constraints.html),
  [partial indexes](https://www.postgresql.org/docs/current/indexes-partial.html), and
  [logical replication](https://www.postgresql.org/docs/current/logical-replication.html)
  — capability evidence behind the database direction.

## Consequences

### For Architecture

Architecture maintains module dependency direction and decides service extraction only
from authority, failure, scale, or upgrade evidence. Every later baseline distinguishes
invariants, defaults, and concrete choices and cites the relevant migration trigger.

### For Integration

Integration owns family-specific compatibility rules, schemas, generated clients,
normalized errors/capabilities, version negotiation, and conformance matrices. External
standards and provider types terminate in adapters. CloudEvents import/export uses the
documented extension mapping and never establishes tenant authority.

### For Security

Security verifies per-binary dependency closure, peer/tenant authority, broker and plugin
isolation, secret/redaction paths, and protected-action audit durability. It must not
describe Agnest 1.0 audit as tamper-evident. New brokers, workflow engines, remote workers,
and third-party plugin hosts are new trust boundaries requiring explicit analysis.

### For Data Design

Data Design carries explicit ownership from the first applicable schema, maintains
separate event, transition, and audit semantics, defines canonical serialization and
content/encryption references, and keeps every intelligence store rebuildable. Physical
schemas enforce the ownership discriminator and tenant-identifier relationship rather
than relying on null or naming conventions.

## Options considered

| Option | Why not |
|---|---|
| Decide only invariants and defer every named technology | The issue requires actionable default directions; language, database, and public-contract changes compound across releases even behind interfaces. |
| Select the complete MVP8 platform now | Kafka/NATS/Temporal, Kubernetes, object storage, remote workers, and specialized indexes add trust zones and operating cost without evidence in MVP1. |
| Microservices from MVP1 | Network and deployment boundaries would be chosen before independent authority/scale/failure needs exist. The modular monolith preserves extraction seams. |
| SQLite for MVP1, migrate later | Concurrent reconciliation and interactive writes plus transactional guards arrive immediately; migration is most expensive after durable histories accumulate. |
| One universal IDL/version number | Public API, protobuf, immutable events, capabilities, database migrations, and plugins have materially different compatibility mechanics. |
| CloudEvents as the internal domain model | It does not own Agnest tenant authority, aggregate ordering, causation, idempotency, or replay semantics. A lossless edge mapping provides portability without surrendering identity. |
| In-process third-party plugins | The control plane would inherit the trust and dependency surface of the least-trusted plugin. |
| External workflow engine as the default | It creates a new high-value trust zone and duplicates product-specific intent/reconciliation semantics before a measured need. |
| Hash-chain audit in MVP1 | Without a trusted verifier/checkpoint and a relevant adversary it does not substantiate tamper evidence and introduces serialization, retention, and recovery complexity. |
| One binary and one dependency tree | It makes `ADR-0003` process boundaries share the attack surface of the web application. |

## Unresolved questions

None. All four roles converged in Issue #13. Customer-managed keys, cryptographic audit,
remote providers/workers, specialized indexes, and external workflow/message systems are
deliberately deferred decisions with triggers, not surviving disagreements.

## Verification

- The MVP1 Implementation Baseline issue is created only after this ADR is accepted and
  selects exact technology versions/tools within the three decision levels.
- Dependency/architecture tests fail if broker binaries import control-plane web, ORM,
  forge, inference, UI, or template stacks; each shipped binary has a distinct SBOM.
- Public OpenAPI, protobuf, events, capabilities, database migrations, and plugin
  protocols have owned compatibility tests using their family-specific rules.
- Tenant-owned records and messages enforce ownership scope; global records are explicit;
  tests reject tenant selection from untrusted payloads or locators.
- PostgreSQL transaction tests cover concurrent interactive/reconciliation writers,
  guards, partial uniqueness, transition/audit co-writes, intent, and outbox behavior.
- Blob tests verify algorithm-qualified content references, corruption detection,
  explicit encryption scheme, and backend-independent metadata references.
- Event conformance proves CloudEvents mappings, extension-name constraints, untrusted
  inbound tenant handling, and rejection of unordered imports as replay authorities.
- Audit tests prove append/order/durability, gaps-permitted sequence semantics, and the
  unknown-outcome path when a required append fails after a possible external effect;
  product and operational docs claim neither deletion detection nor MVP1/1.0 tamper
  evidence.
- Plugin and adapter tests prove serialization, capability negotiation, least authority,
  cancellation, resource bounds, normalized failures, and out-of-process third-party
  isolation.
- Upgrade tests model ordered retryable partial states, mixed-version gates, scoped
  capability invalidation, backup/restore, and expand/migrate/switch/contract.
- Projection tests rebuild from canonical versions and compare provenance before a new
  search/graph/vector backend becomes authoritative for reads.
- Operational docs deploy only the services needed by the current MVP and cite a measured
  trigger plus later ADR for every added trust zone or distributed dependency.
