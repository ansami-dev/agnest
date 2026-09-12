# PRD — MVP 8: Governance, Enterprise Security & Scale

## 1. Purpose

Evolve the platform from a powerful single-team engineering control plane into a governed multi-team platform. Add organization/project tenancy, RBAC/ABAC-style policy, secret broker, network/sandbox policy, quotas, audit/compliance, retention, resilience, high availability, administrative controls, and enterprise-grade observability.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Support multiple users/teams/projects with explicit authorization boundaries.
- Enforce agent, tool, repository, sandbox, model/provider, secret, and publish policies centrally.
- Introduce secret broker and short-lived credential patterns.
- Define sandbox/network policy profiles and high-risk execution isolation.
- Add organization/project quotas and spend controls.
- Provide complete audit trail and exportable compliance evidence.
- Add HA/resilience, background-job durability, backups, disaster recovery, and scale controls.
- Support policy-governed automation while preserving human override and approval.
- Add retention/deletion controls for source-derived indexes, transcripts, artifacts, logs, and workspaces.

## 4. Non-Goals

- Generic enterprise IAM product replacement.
- Production application deployment orchestration beyond software-delivery handoff.
- Full SIEM/SOAR replacement.
- Guarantee of compliance certification by product behavior alone.

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Team isolation
Two teams use same deployment but cannot view or query each other's repos, agents, context packs, artifacts, or credentials.

### W2 — Policy-controlled task
Security-sensitive repository requires VM sandbox, approved model provider, no external MCP, and human publish approval. Policy selects/enforces those constraints automatically.

### W3 — Spend guardrail
Organization sets monthly model budget and per-task frontier limit. Workflow warns/throttles/blocks according to policy.

### W4 — Audit/compliance
Auditor reconstructs who assigned task, which agent/harness/model/context acted, workspace/commit lineage, reviews, approvals, publish, and remote PR.

## 7. Functional Requirements

- **FR-M8-001 Organization/team/project tenancy:** hierarchical ownership and membership.
- **FR-M8-002 RBAC:** predefined/custom roles for admin, developer, reviewer, security, auditor, operator.
- **FR-M8-003 Resource authorization:** project/repo/agent/group/task/workspace/artifact/integration permissions.
- **FR-M8-004 Policy engine:** conditions over repository classification, task type, agent role, sandbox class, provider trust, action type, finding severity.
- **FR-M8-005 Sandbox policy profiles:** resource, privilege, network, filesystem, provider minimum isolation.
- **FR-M8-006 Network egress policy:** allow/deny destinations/classes with auditable exceptions.
- **FR-M8-007 Secret broker:** scoped retrieval/injection, short-lived credentials where integration supports, rotation and revocation.
- **FR-M8-008 Protected action policy:** commit/publish/PR/merge/tool/secret/model escalation approvals.
- **FR-M8-009 Budget/quota:** tokens/cost/concurrency/workspaces/sandbox resources per org/project/user/agent.
- **FR-M8-010 Audit log:** immutable append-oriented record of security/engineering/control actions.
- **FR-M8-011 Audit export:** filtered export with integrity metadata.
- **FR-M8-012 Retention policy:** workspaces, logs, transcripts, context packs, artifacts, indexes, usage records.
- **FR-M8-013 Data deletion:** authorized deletion workflow including derived intelligence where required.
- **FR-M8-014 HA control plane:** stateless/API scaling and durable coordination state.
- **FR-M8-015 Worker/sandbox scale:** distributed workers and placement by capability/policy.
- **FR-M8-016 Backup/restore:** database, configuration, key metadata, artifact/index recovery strategy.
- **FR-M8-017 DR:** documented RPO/RTO targets and recovery runbook.
- **FR-M8-018 Admin dashboard:** health, queues, stuck tasks, spend, integration health, policy violations.
- **FR-M8-019 Security alerts:** credential failure, denied action, unusual spend, sandbox policy violation, repeated publish failure.
- **FR-M8-020 SSO/OIDC integration:** enterprise authentication baseline.
- **FR-M8-021 Service identities:** non-human agents/integrations use scoped service identity.
- **FR-M8-022 Policy simulation:** preview whether proposed task/runtime/publish will be allowed and why.
- **FR-M8-023 Compliance evidence bundle:** task-to-PR lineage with reviews/approvals/runtime/model/context metadata.
- **FR-M8-024 Concurrency/resource scheduler:** fair scheduling and quotas across teams.
- **FR-M8-025 Upgrade/migration support:** schema/config/index migration visibility and rollback strategy.

## 8. Non-Functional Requirements

- High availability target and SLOs must be defined per deployment tier.
- Authorization decision latency must not materially degrade interactive UI.
- Audit writes for protected actions must be durable before action is considered complete.
- Policy decisions must be explainable.
- Tenant boundaries apply to search/index/context, not only UI/API records.
- Backup/restore procedures must be tested.
- Secret values must never appear in audit logs.
- Distributed workers must tolerate transient network partition without duplicate protected actions.

## 9. Domain Entities and Data Considerations

Entities: `Organization`, `Team`, `Membership`, `Role`, `Permission`, `Policy`, `PolicyVersion`, `PolicyDecision`, `ResourceClassification`, `SecretRef`, `SecretLease`, `Budget`, `Quota`, `UsageAggregate`, `AuditEvent`, `RetentionPolicy`, `DeletionJob`, `WorkerNode`, `WorkerCapability`, `PlacementDecision`, `SecurityAlert`, `BackupRecord`.

Authorization and policy decisions should be versioned and referenced by protected actions for later explanation. Tenant ID/ownership must be explicit in all primary data and indexes.

## 10. Integration Requirements

- OIDC/SSO provider.
- Secret manager/Vault-style backend abstraction.
- SIEM/log export.
- Metrics/tracing stack.
- Distributed sandbox workers.
- Object/artifact/index storage.
- Backup infrastructure.
- Optional enterprise Git/org integrations.

## 11. Security and Trust Requirements

- Formal threat model for multi-tenant control plane and workers.
- Strong tenant isolation in primary DB, object storage, graph/vector/lexical indexes, caches, logs.
- Policy enforcement at server side; UI is not a security boundary.
- Secret broker with scoped leases, rotation, revocation, zero plaintext logging.
- Sandbox privilege/network profiles and policy-enforced provider choice.
- Provider/model trust and data-residency policy.
- Tamper-evident/append-oriented audit strategy.
- Break-glass admin access with enhanced audit.
- Approval separation-of-duties for high-risk repositories/actions.
- Supply-chain security for runtime images/adapters/plugins.
- Worker identity/mTLS or equivalent authenticated control channel.

## 12. Architecture Considerations and Constraints

- Introduce tenancy/policy without rewriting core single-project semantics: all prior resources gain ownership scope.
- Authorization should be centralized and callable by all services.
- Policy engine should be deterministic/explainable and versioned.
- Protected actions use transactional/outbox patterns so audit and side effects remain consistent.
- Distributed workers require leases/idempotency for task execution.
- Search/index systems require tenant-aware partitions/filters.
- Design HA topology, queue/event durability, object storage, and recovery as platform concerns.

## 13. Observability and Telemetry

Capture SLOs, auth failures, denied actions, policy decision latency/outcomes, secret leases, sandbox/network violations, budget usage, per-tenant concurrency, queue depth, stuck tasks, worker health, audit pipeline lag, backup/restore status, DR tests, provider spend anomalies.

## 14. Acceptance Criteria

- Two tenants cannot access each other's API data, source-derived indexes, context packs, artifacts, or logs under adversarial tests.
- Policy forces high-risk project onto VM sandbox and approved model provider.
- Publish requiring two roles cannot be self-approved by implementation agent/user lacking second role.
- Secret lease expires/revokes and is absent from sandbox/logs afterward.
- Budget limit blocks or downgrades model route according to configured policy.
- Auditor reconstructs full task-to-PR lineage with policy decisions and approvals.
- Restore from backup into clean environment and recover active metadata to documented RPO.
- Worker failure does not duplicate remote publish or protected action.
- Policy simulation explains allow/deny before execution.

## 15. Dependencies

All previous MVPs; stable resource ownership IDs; secrets manager; OIDC; distributed runtime/sandbox workers; observability/storage stack.

## 16. Risks and Mitigations

- **Tenant data leak:** pervasive ownership keys, service-level authz, index partition tests.
- **Policy complexity:** explainable rules, simulation, versioning, safe defaults.
- **Secret leakage:** broker/leases/redaction and no direct DB plaintext.
- **Distributed duplicate actions:** leases/idempotency/outbox.
- **Operational complexity:** deployment profiles, health diagnostics, tested backup/DR.
- **Cost runaway:** quotas/budgets/concurrency controls and alerts.

## 17. Open Questions

1. RBAC only or RBAC + attribute/policy conditions?
2. Which policy engine approach (embedded vs external) best preserves explainability and portability?
3. Default retention for transcripts/context/source-derived embeddings?
4. Required RPO/RTO deployment tiers?
5. How are BYOK/customer-managed keys handled?
6. What constitutes tamper-evident audit sufficient for target regulated users?
7. When may policy auto-publish without human approval?

## 18. Handoff — Architect Agent

Design multi-tenant service/data architecture, centralized authorization/policy service, worker scheduling/placement, HA/event durability, secret-broker integration, transactional protected actions, backup/DR topology, and migration path from single-node deployments. Define deployment tiers and failure domains.

## 19. Handoff — Security Agent

Produce enterprise threat model, tenant isolation controls, RBAC/policy matrix, secret lifecycle, worker identity, mTLS/network controls, sandbox profiles, provider trust/data residency, audit integrity, SoD, break-glass, supply-chain controls, and security test plan.

## 20. Handoff — Integration Agent

Specify OIDC/SSO, secret-manager, SIEM/log export, metrics/tracing, distributed worker protocol, enterprise Git org integration, backup/object storage, and provider policy integration. Define health/credential rotation/failure behavior for each.

## 21. Handoff — Data Design Agent

Define ownership/tenant propagation for all prior entities, RBAC/policy schemas and versioning, audit/event structure, secret references/leases, quotas/usage aggregates, worker/placement state, retention/deletion workflow, backup metadata, and partition/index strategy to prevent cross-tenant leakage.
