# Cross-MVP Traceability Matrix

## 1. MVP Dependency Graph

```text
MVP1 Git Foundation & Workspaces
  ↓
MVP2 Agent Runtime Fabric
  ↓
MVP3 Orchestration & Groups
  ↓
MVP4 Review / Quality / Publish
  ↓
MVP5 Repository Intelligence
  ↓
MVP6 Context Intelligence & Token Economics
  ↓
MVP7 Integrations & Inference Fabric
  ↓
MVP8 Governance / Enterprise / Scale
```

The sequence is intentionally cumulative, but selected implementation work may proceed in parallel once stable interfaces exist. For example, repository indexing prototypes can begin during MVP3/4, while production integration is formally accepted in MVP5.

## 2. Product Principle Traceability

| Principle | MVP1 | MVP2 | MVP3 | MVP4 | MVP5 | MVP6 | MVP7 | MVP8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Harness agnostic |  | Primary | Reinforced | Reinforced |  | Reinforced | Expanded | Governed |
| Sandbox agnostic | Primary | Reinforced |  |  |  |  |  | Governed/Scaled |
| Model agnostic |  | Baseline |  |  |  | Telemetry | Primary | Governed |
| Git native | Primary | Reinforced | Workspace link | Primary | Source truth | Source verification | Provider expansion | Governed |
| A2A native |  | Primary | Primary | Review task use |  | Escalation contract | Interop expansion | Policy |
| Artifact driven |  | Baseline | Primary | Primary | Provenance | Context reuse | Integration events | Audit |
| Context efficient |  |  | Artifact reuse | Review targeting | Intelligence substrate | Primary | Gateway optimization | Budget policy |
| Source verified | Git canonical |  |  | Diff/source | Primary | Primary |  | Audit/evidence |
| Local-first remote-by-approval | Primary |  | Approval foundation | Primary |  |  | Git integration | Policy/SoD |

## 3. Core Domain Entity Introduction

| Entity | Introduced | Expanded |
|---|---|---|
| Project | MVP1 | MVP8 tenancy |
| Repository | MVP1 | MVP5 intelligence, MVP7 provider |
| Workspace | MVP1 | MVP4 review, MVP5 overlay |
| Sandbox | MVP1 | MVP8 policy/placement |
| Agent | MVP2 | MVP3 group, MVP8 permissions |
| RuntimeBinding/Session | MVP2 | MVP7 inference/provider |
| Task | MVP3 | MVP6 context, MVP8 quota/policy |
| Group | MVP3 | MVP8 org governance |
| Artifact/Finding/Decision | MVP3 | MVP4 review, MVP6 context reuse |
| Approval | MVP3 | MVP4 publish, MVP8 SoD/policy |
| Review/QualityGate | MVP4 | MVP8 policy |
| PullRequest/CIStatus | MVP4 | MVP7 providers |
| RepositoryIndex/Symbol/Relationship | MVP5 | MVP6 context |
| ContextPack | MVP6 | MVP8 retention/audit |
| InferenceProvider/ModelPolicy | MVP7 | MVP8 trust/budget |
| Organization/Policy/Audit/Quota | MVP8 | — |

## 4. Specialist Agent Deliverables by MVP

### Architect
- MVP1: Git/workspace/sandbox service boundaries and recovery.
- MVP2: runtime adapter/A2A architecture and failure isolation.
- MVP3: durable task/event/workflow architecture.
- MVP4: local-to-remote publication architecture.
- MVP5: repository intelligence/index/overlay design.
- MVP6: context engine/retrieval/budget/escalation design.
- MVP7: integration plugin and inference fabric architecture.
- MVP8: tenancy/policy/HA/distributed worker architecture.

### Security
- MVP1: sandbox/Git credential trust boundary.
- MVP2: runtime/provider credential and adapter trust.
- MVP3: delegation, approval, agent-to-agent injection threats.
- MVP4: publish authority, webhooks, review/waiver controls.
- MVP5: source/index/IP/privacy controls.
- MVP6: retrieved-content prompt injection and sensitive-context controls.
- MVP7: provider trust, MCP permissions, safe fallback, secret rotation.
- MVP8: tenancy, policy, secret broker, SoD, audit, worker security.

### Integration
- MVP1: Forgejo/GitHub read/fetch and local Incus system-container contract; OCI/VM modes are capability-gated.
- MVP2: Hermes/Claude Code/Codex/OMP adapters and A2A mapping.
- MVP3: orchestration events/A2A artifacts.
- MVP4: Forgejo/GitHub write/PR/CI webhooks.
- MVP5: parsers, graph/vector/lexical backends, Graphify optional adapter.
- MVP6: context/retrieval/reranker/compressor contracts.
- MVP7: full Git/MCP/CI/inference provider plugin set.
- MVP8: OIDC, secret manager, SIEM, distributed worker integrations.

### Data Design
- MVP1: repository/workspace/sandbox/test schemas.
- MVP2: agent/runtime/session/execution/capability schemas.
- MVP3: task/workflow/artifact/event/approval schemas.
- MVP4: review/gate/commit/publish/PR/CI schemas.
- MVP5: symbol/relationship/index/provenance/overlay schemas.
- MVP6: context plan/pack/token/cost/quality lineage schemas.
- MVP7: provider/model/route/tool/usage schemas.
- MVP8: tenancy/policy/audit/quota/retention/worker schemas.

## 5. Validation Strategy Across Roadmap

Every MVP should produce:

1. Product acceptance test suite against PRD acceptance criteria.
2. Architecture Decision Records for major implementation choices.
3. Threat model delta and security test cases.
4. Integration conformance tests for each provider/adapter introduced.
5. Data migration/versioning plan for schema changes.
6. Operational runbook for failure and recovery.

From MVP5 onward, maintain a repeatable benchmark repository/issue set measuring:

- baseline harness-only token usage;
- platform-assisted token usage;
- task completion;
- tests passed;
- review findings;
- rework loops;
- latency and cost.

No token-saving feature should be promoted solely on lower token count if engineering quality materially regresses.
