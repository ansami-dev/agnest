# ADR-0019: Fix the MVP1 implementation baseline for the Ubuntu appliance

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-09-14 |
| **MVP** | M1 |
| **Coordinator** | Architecture (Codex) |
| **Originating issue** | #19 |
| **Supersedes** | none |
| **Requirements** | `FR-M1-001`–`FR-M1-020`, `NFR-M1-001`–`NFR-M1-008` |

## Context

`ADR-0003` fixes the MVP1 authority boundaries, `ADR-0011` selects local Incus as
the sole MVP1 sandbox provider, and `ADR-0013` fixes the product-wide technology
direction and its evolution seams. MVP1 still needs one reproducible implementation
baseline: exact platforms, versions, libraries, generators, source layout, packaging,
storage isolation, and release evidence.

Selecting only convenient tools would leave the accepted security and durability
boundaries as prose. Freezing every version indefinitely would instead make security
maintenance impossible. This decision therefore distinguishes:

- the sole Release Ready platform;
- exact bootstrap pins used to reproduce the first implementation;
- supported patch lines and compatibility rules; and
- evidence-based triggers for changing a component without reopening product identity.

Issue #19 reached specialist consensus after two rounds. The Product Owner then limited
the release contract to Ubuntu Server 26.04 LTS on `amd64`. Windows, `arm64`, and other
hosts or architectures are not support tiers or roadmap commitments; they require
demonstrated demand and a later decision with live conformance evidence.

## Decision

### 1. Support one reference appliance

MVP1 is Release Ready only on **Ubuntu Server 26.04 LTS `amd64`** with current security
updates. The bootstrap and supported lines are:

| Concern | Bootstrap pin | Supported policy |
|---|---|---|
| Appliance image | Ubuntu Server 26.04.1 LTS, `amd64` | Ubuntu 26.04 LTS security-update line only |
| Service manager | systemd 259 | OS-supplied version |
| Incus | 7.0.1 LTS | Incus 7.0.x LTS; other lines require separate evidence |
| PostgreSQL | 18.6 | PostgreSQL 18.x current minor |
| Native Git | Ubuntu package 2.53.0-1ubuntu1 | OS-supported Git 2.53.x packages |
| Go | minimum 1.26.5; release toolchain 1.27.1 | Supported security-patched toolchain only |
| Browser build runtime | Node.js 24.21.0 LTS | Node 24 LTS; build/test only |
| JavaScript package manager | pnpm 11.26.0 | Exact `packageManager` pin and committed lockfile |

The reference VM has 4 vCPU, 8 GiB RAM, SSD-backed storage, and at least 100 GiB free
for fixtures after the required recovery reserve is excluded. These resources define
repeatable measurement conditions, not a universal minimum installation size.

Incus system containers are required. OCI application containers and Incus VMs remain
capability-gated as fixed by `ADR-0011`; lack of an optional kind does not make the
required system-container baseline unhealthy.

### 2. Use one Go module with independently deliverable authorities

The repository starts with one Go module and this source layout:

```text
/api/openapi/                 canonical public REST/SSE contract
/api/proto/agnest/.../v1/     canonical broker protobuf contracts
/cmd/agnestd/                 control-plane binary
/cmd/agnest-fetch-broker/     credentialed Git fetch authority
/cmd/agnest-incus-broker/     Incus lifecycle/exec authority
/internal/domain/             dependency-free domain behavior
/internal/app/                use cases and ports
/internal/adapters/           PostgreSQL, Git, blob, HTTP implementations
/internal/brokers/            broker implementations; forbidden to agnestd
/internal/store/sqlc/         checked-in generated query code
/db/migrations/               ordered SQL-only migrations
/db/queries/                  sqlc source queries
/gen/go/                      checked-in OpenAPI/protobuf generated code
/web/                         browser application and generated TypeScript client
/deploy/systemd/              units, tmpfiles, sysusers, credential declarations
/packaging/                   package metadata and upgrade hooks
/test/{contract,conformance,e2e,fixtures}/
/tools/                       pinned generators and verification entry points
```

One module does not merge the authorities. The release produces independently versioned
`agnest-control`, `agnest-fetch-broker`, `agnest-incus-broker`, and `agnest-web`
packages, plus an `agnest` meta-package that pins a compatible set. Every binary has a
separate reachable-dependency manifest, vulnerability result, SBOM, artifact digest,
systemd unit, restart path, and deployment decision.

An unaffected broker is not deployed or restarted for a control-plane-only change when
its source, reachable dependencies, generated RPC, toolchain, and artifact inputs are
unchanged. Broker binaries use reproducible build inputs, `-trimpath`, and disabled VCS
stamping. Source revision and provenance remain external package/build metadata.

The Go module must split before release if dependency versions diverge, unchanged-input
proof is impossible, a security fix cannot be delivered to one authority independently,
or ownership/release cadence separates.

### 3. Fix the Go application and persistence stack

- HTTP uses Go `net/http` with generated strict OpenAPI interfaces; no general web
  framework is introduced.
- PostgreSQL access uses `pgx/v5` 5.11.0, `sqlc` 1.31.1, and explicit SQL. No ORM or
  in-memory database substitutes for PostgreSQL integration evidence.
- Ordered SQL-only migrations use `goose` 3.28.0. Production migrations are
  forward-only and never run silently at application startup. Recovery uses retry,
  forward repair, or restore plus reconciliation rather than destructive down migration.
- RPC uses `grpc-go` 1.83.2 and `protobuf-go` 1.36.12 behind generated ports.
- Only the Incus broker imports `github.com/lxc/incus/v7`, pinned to 7.0.1.
- Structured logs use `log/slog`; OpenTelemetry Go 1.46.0 begins at the control-plane
  boundary. Prometheus is the initial metrics export. Audit is not a telemetry stream.
- Each process reads one strict typed TOML document. Unknown keys are fatal. Precedence is
  defaults, file, explicitly allowed environment overrides, then flags. Secrets are
  references delivered through systemd credentials or broker-only root-owned files, never
  values in general configuration.

The persistence layer must express partial unique indexes, coupled-column `CHECK`
constraints, guarded updates with affected-row results, and deterministic
`SELECT ... FOR UPDATE SKIP LOCKED` leases directly. Co-occurring transition, outbox,
and audit writes use one explicit PostgreSQL transaction. Error classification uses
SQLSTATE and named constraints, never localized message text.

Application startup checks schema compatibility but does not mutate the schema. The
controlled upgrade path supports the immediately previous released schema during its
expand, migrate, switch, and contract sequence.

### 4. Make every generated boundary a reproducible pipeline

The public API is OpenAPI 3.1.1 YAML. `oapi-codegen` 2.8.0 generates strict Go
`net/http` interfaces; `openapi-typescript` 7.13.0 and `openapi-fetch` 0.17.0 provide
the browser transport types behind a handwritten client. SSE remains a handwritten
one-way activity port with reconnect and `Last-Event-ID`; MVP1 does not add WebSocket.

Broker schemas use proto3 and separately versioned packages such as
`agnest.broker.fetch.v1` and `agnest.broker.sandbox.v1`. Buf 1.73.0,
`protoc-gen-go` from protobuf-go 1.36.12, and `protoc-gen-go-grpc` aligned with
grpc-go 1.83.2 form the pinned local generator pipeline. Release generation does not
fetch floating remote plugins. Removed protobuf fields reserve both number and name;
unknown enum and capability values survive transport and fail closed at policy decisions.

Generated source is committed and never edited by hand. Domain packages never import
generated DTOs. A contract change must pass schema validation, examples, semantic
compatibility classification, generation, compilation/type checking, and a clean
regeneration diff. Additive public changes remain in `v1`; semantic breaks require a new
public major and an overlap period.

Durable events remain versioned Agnest-native canonical JSON. Protobuf remains an RPC
encoding. Identity, correlation, causation, tenant scope, and version semantics are
defined once normatively and mapped explicitly into both encodings.

### 5. Use narrow native adapters

Native Git is invoked with an argument array, fixed locale and configuration isolation,
explicit deadlines, bounded standard I/O, and no shell. Machine output uses porcelain v2
with NUL delimiters or documented plumbing, never human prose or color output. GitHub and
Forgejo use narrow typed clients built on `net/http`; host-specific authentication,
redirect, pagination, rate-limit, and error behavior stops at the adapter.

The Incus broker uses the official local Unix API client and explicit extension discovery.
It never shells out to or parses the Incus CLI. Capability evidence is recorded per
instance kind and is re-established after relevant client, daemon, adapter, or host
changes.

Every control-plane filesystem operation below an allocated Workspace root uses Go
`os.Root`, including in-root quarantine through `Root.Rename`. Clean-plus-prefix checks
are non-conforming. Mount traversal is outside `os.Root`'s guarantee and is separately
denied by the Incus/systemd security profile.

Native Git receives extra containment because it resolves paths in another process. Its
adapter derives the Workspace root only from authoritative state, opens and holds that
root, revalidates identity at dispatch, launches Git from a proven descriptor-rooted
working directory, sets `GIT_CEILING_DIRECTORIES`, disables hooks and system/global
configuration, and retains the descriptor through completion. Untrusted strings cannot
become `--git-dir`, `--work-tree`, or any independently re-resolved path. A Linux race
spike must pass `NFR-M1-005` before path-bearing Git operations are implemented; there is
no string-prefix fallback.

### 6. Use a small browser implementation behind the public contract

The browser application uses TypeScript 7.0.2 in strict mode, React/React DOM 19.3.0,
Vite 8.3.0, React Router 8.3.1, and TanStack React Query 5.102.8. Vitest 5.0.0,
Testing Library React 16.3.3, and Playwright 1.63.0 provide browser tests.

React Query owns replaceable server-state caching, not lifecycle truth. Router state is
navigation state; durable workflow state comes from API/SSE projections. Local component
state uses React primitives before another global state library is justified. The UI
starts with semantic HTML, accessible primitives, and CSS Modules rather than a component
suite or CSS runtime.

Content-hashed static assets are embedded in and served by `agnestd`. Node and pnpm are
absent from the runtime appliance. The public UI contract supports the current and previous
stable Chrome, Edge, and Firefox releases plus current Safari, gated through Playwright's
Chromium, Firefox, and WebKit engines.

### 7. Express authority boundaries in systemd

The control plane, fetch broker, and Incus broker run as distinct service users and units.
The control plane is never a member of `incus-admin`; only the Incus broker receives local
Incus socket authority. Fetch credentials use `LoadCredential=` or an equivalently scoped
systemd credential path and must not appear in environment variables, arguments, Git
configuration, logs, or RPC results.

The four independently versioned components ship as `.deb` packages built with nfpm;
checksummed tar archives are inspection artifacts, not a second supported installation
method. PostgreSQL and Incus remain separately patched OS services rather than being
embedded or containerized by Agnest. Package installation does not start a destructive
migration automatically.

Each unit begins with `NoNewPrivileges=yes`, `ProtectSystem=strict`, `ProtectHome=yes`,
`PrivateTmp=yes`, explicit writable paths and address families, a reduced
`CapabilityBoundingSet`, and a syscall allow/deny policy. Issue #23 fixes the exact
per-authority policy; Issue #27 owns operational thresholds and recovery.

Local gRPC uses Unix-domain sockets. Filesystem permissions are necessary but not
sufficient: the broker reads `SO_PEERCRED` at connection acceptance and authorizes the
authenticated UID through a server-owned caller map. PID is diagnostic context only and
never an authorization identity. Caller-supplied identity metadata is untrusted.

Credential, token, remote-URL, environment-value, and command-output types redact at the
structured log/telemetry sink. Secret-bearing types do not expose revealing string
formatting, and a second handler layer redacts allowlisted sensitive classes. Raw command
output is bounded artifact data and is not logged by default.

### 8. Separate five storage consumers and retain recovery capacity

A single unconstrained root filesystem is unsupported. The appliance provides five
independently bounded consumers:

1. OS/root, including journald, systemd state, private temporary space, and application
   scratch; journald has an explicit size cap;
2. PostgreSQL data and WAL;
3. the content-addressed blob root;
4. Git mirrors, worktrees, and quarantine; and
5. the Incus storage pool.

The four data consumers use thick-provisioned logical volumes/filesystems. Thin
provisioning is excluded unless shared-pool exhaustion is later specified and tested as
the governing failure boundary. At least 10% of the data volume group remains unallocated
as operator recovery capacity.

The per-volume boundary is the runtime guard measured by `NFR-M1-008`; unallocated VG
space is a manual recovery lever and is not consumed automatically. Filling Git/workspace
or Incus capacity cannot breach PostgreSQL or blob capacity, and filling blob capacity
cannot breach PostgreSQL. Exact volume sizes, alerts, extension, and recovery procedures
belong to Issue #27; per-Sandbox quotas and security policy belong to Issue #23.

### 9. Fix durable identifiers and canonical evidence

- Primary entity IDs are application-generated UUIDv7 values, serialized as lowercase
  hyphenated text and stored as PostgreSQL `uuid`. Approximate creation-time disclosure is
  accepted for the personal-appliance scope; identity is never treated as authorization.
  The initial Go library is `github.com/google/uuid` 1.6.0.
- Content references use SHA-256 from the standard library and carry algorithm and format
  version. Hex casing and content framing are contract-defined.
- Audit sequence uses a PostgreSQL identity `bigint`: strictly increasing per deployment,
  with gaps permitted and no claim that absence proves deletion.
- Audit canonicalization is RFC 8785 JCS, identified as `jcs-rfc8785` format version 1.
  The initial Go library is `github.com/gowebpki/jcs` 1.0.1 behind a canonicalizer port.
  Canonical bytes are stored at append time and never reconstructed as historical evidence.
- Every int64-domain value in canonical JSON is encoded as a decimal JSON string,
  including audit sequences, byte counts, nanosecond durations, and future int64 fields.
  Fixtures include values above `2^53`. Small explicitly bounded integers may remain JSON
  numbers.

Canonical bytes preserve deterministic evidence but do not add a cryptographic or
tamper-evidence claim beyond `ADR-0013`.

### 10. Gate releases on evidence

The test topology is:

1. schema validation, compatibility, clean regeneration, Go compilation, and TypeScript
   type checking;
2. deterministic adapter fixtures and real PostgreSQL integration tests;
3. live Forgejo, PostgreSQL, native Git, and per-kind Incus conformance on the reference VM;
4. failure injection at intent/effect/observation boundaries; and
5. browser end-to-end tests through the generated public client.

The existing `CONF-M1-*` catalogue and `NV-M1-*` protocols remain the identifiers; tools
do not create a parallel numbering scheme. Required gates include:

- Linux `os.Root` hostile-path and descriptor-rooted Git race cases;
- broker hardening inspection and wrong-UID peer denial before effects;
- credential absence from `/proc/<pid>/environ`, arguments, config, logs, telemetry, and
  returned fields;
- all four PostgreSQL constraint/query shapes and SQLSTATE mapping;
- per-binary dependency closure, forbidden imports, vulnerability report, SPDX JSON SBOM,
  reproducibility, unchanged-input proof, and package deployment evidence;
- RFC 8785 official vectors, values above `2^53`, and stored-byte stability across an N-1
  upgrade rehearsal;
- independent Git/workspace and Incus capacity exhaustion while PostgreSQL, blob, and
  control-plane probes remain healthy; and
- package install, controlled upgrade, interrupted upgrade/retry, backup/restore, remove,
  and forward-repair smoke tests.

The pinned release tools are `golangci-lint` 2.13.2, nfpm 2.47.0, Syft 1.51.1, and
Cosign 3.1.3 in addition to the generators already named. Inputs and hashes live in one
checked-in toolchain/appliance manifest. Release outputs include checksummed inspection
archives, per-binary and frontend SBOMs, signatures, and provenance. A skipped required
tier is `BLOCKED`, not passed.

The minimum Go patch moves immediately when a security-sensitive standard-library
primitive requires a fixed patch. A supported-line security update is an ordinary reviewed
change after the full applicable gates pass. Major dependency, PostgreSQL major, Go
language-baseline, Incus LTS, contract-generator, or packaging-format changes require a
compatibility assessment and a successor ADR when they change accepted semantics or
operations. A vulnerable or end-of-life pin forces migration; reproducibility never
justifies retaining it.

## Consequences

### For Architecture

MVP1 gains one concrete deployment and source topology while retaining the ports and
triggers required by `ADR-0013`. Architecture must keep process authority, storage
capacity, generated-edge, and domain dependency boundaries executable rather than
conventional.

### For Integration

Integration owns reproducible schema pipelines, compatibility classification, native
adapter fixtures, and live conformance against the pinned Ubuntu, Git, PostgreSQL, Incus,
and browser matrix. No remote provider, workflow engine, message broker, ORM, broad forge
SDK in a privileged broker, or floating generator enters MVP1; the Incus broker's pinned
official client is the deliberate narrow exception.

### For Security

Issue #23 must turn the systemd, IPC identity, credential custody, mount, storage quota,
network, and redaction requirements into `THR-M1-*` and `SEC-M1-*` controls. Security can
reject an implementation that has the named tools but not the kernel- and OS-visible
boundary evidence.

### For Data Design

Issue #22 must define the physical schema and the single normative identity/correlation/
causation/tenant/version semantics shared by JSON events and protobuf RPC. It must preserve
forward-only history, stored canonical bytes, int64 string encoding, UUIDv7 identity, and
transaction-visible constraints.

## Options considered

| Option | Why not |
|---|---|
| Support Windows or `arm64` in MVP1 | The Product Owner chose one evidenced Ubuntu `amd64` release target. Other platforms are demand-driven decisions, not partial support promises. |
| Multiple Go modules from the first scaffold | Separate packages, reachable-dependency evidence, and reproducible artifacts provide independent patch/restart behavior with less solo-project friction. Explicit triggers force a split when that proof stops holding. |
| General Go web framework or ORM | Neither is needed for MVP1; both obscure the small HTTP boundary or SQL invariants and enlarge privileged dependency closures. |
| Persist protobuf events | RPC field evolution and immutable event history require different compatibility mechanics. They share semantics, not storage encoding. |
| Incus CLI or provider SDKs throughout the application | CLI prose is not a contract, and broad SDK types would cross authority/adapter boundaries. |
| Hand-rolled cleaned-path prefix checks | They cannot satisfy the rename/symlink race oracle and do not confine a separately resolving Git child process. |
| One unconstrained filesystem or thin-provisioned shared pool | Exhaustion by untrusted work could deny writes to PostgreSQL, blobs, or the host despite apparent per-volume separation. |
| Environment-variable credentials | They weaken custody and can appear through process inspection, diagnostics, and crash tooling. |
| Down migrations for durable history | Automatic reversal can destroy append-only transition, event, outbox, or audit evidence. |
| JSON numbers for int64-domain values | RFC 8785 follows IEEE-754/ECMAScript number semantics and cannot preserve every integer above `2^53`. |

## Unresolved questions

None. Security policy details remain delegated to Issue #23, physical data design to
Issue #22, upgrade/recovery procedures to Issues #26 and #27, and public/RPC contract
details to Issues #24 and #25. Those issues implement this decision; they do not reopen it.

## Verification

A later change violates this ADR when any of the following is true:

- a Release Ready artifact or claim targets a platform other than Ubuntu Server 26.04
  LTS `amd64` without a successor decision and live evidence;
- a privileged binary imports a forbidden application, UI, persistence, forge, or other
  authority implementation dependency;
- rebuilding unchanged broker inputs changes its binary digest or a control-only patch
  requires an unaffected broker restart;
- generated code differs after clean regeneration or generated DTOs enter domain packages;
- a path-bearing operation falls back to string-prefix containment, or Git receives an
  untrusted independently resolved repository path;
- a caller with socket-path access but the wrong UID reaches a broker side effect;
- credential bytes appear in process environment, arguments, Git configuration, logs,
  telemetry, or RPC output;
- real PostgreSQL tests cannot enforce the four required SQL shapes atomically;
- canonical audit bytes change on read/upgrade, or an int64-domain value is encoded as a
  JSON number;
- filling an untrusted storage allocation prevents the required PostgreSQL, blob, or
  control-plane probes; or
- a required live, failure, migration, security, compatibility, or supply-chain gate is
  skipped but the release is reported as passed.

## References

- Originating deliberation: [Issue #19](https://github.com/ansami-dev/agnest/issues/19)
- `ADR-0003`: MVP1 component authority boundaries
- `ADR-0011`: local Incus provider for MVP1
- `ADR-0013`: product-wide technology architecture
- Go path-confinement fix: [GO-2026-4970](https://pkg.go.dev/vuln/GO-2026-4970)
- JSON Canonicalization Scheme: [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785)
