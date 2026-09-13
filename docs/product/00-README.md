# Git-Native Multi-Agent Engineering Control Plane — Product Documentation

This documentation bundle defines the full product vision and staged product requirements for a harness-agnostic, sandbox-agnostic, model-agnostic, Git-native multi-agent software engineering platform.

## Product Principles

1. **Harness agnostic** — Agent identity and workflow are not tied to Hermes, Claude Code, Codex, OMP, or any single runtime.
2. **Sandbox agnostic** — MVP1 implements local Incus behind a stable interface; additional local or remote execution backends are demand-driven choices.
3. **Model agnostic** — Frontier, local, and routed models can be selected by policy without changing the agent identity.
4. **Git native** — Repository, branch, worktree, diff, commit, review, publish, and pull request are first-class product concepts.
5. **A2A native** — Agent interoperability is standardized through Agent2Agent concepts, with adapters for non-native runtimes.
6. **Artifact driven** — Durable state lives in tasks, artifacts, findings, decisions, approvals, commits, and test results rather than chat transcripts.
7. **Context efficient** — Agents receive the minimum sufficient context required for the current task and role.
8. **Source verified** — Derived graph/vector/summary knowledge is never treated as the canonical source over the repository itself.
9. **Local-first, remote-by-approval** — Agents work in isolated local Git workspaces; remote push and PR creation occur only through explicit policy or approval.

## Documents

- `01-product-vision.md` — complete product vision, users, product pillars, architecture layers, lifecycle, roadmap, success measures, and product principles.
- `02-prd-mvp1-git-foundation.md` — Git project/workspace foundation and sandbox lifecycle.
- `03-prd-mvp2-agent-runtime-fabric.md` — agent identity, runtime adapters, A2A interoperability, Hermes/Claude Code/Codex/OMP.
- `04-prd-mvp3-orchestration-groups.md` — tasks, events, artifacts, approvals, deliberation groups, and workflow groups.
- `05-prd-mvp4-review-quality-publish.md` — local diff review, QA/code/security review, quality gates, commit/publish/PR lifecycle.
- `06-prd-mvp5-repository-intelligence.md` — AST/code graph, lexical/vector retrieval, repository indexing, graph-backed impact analysis.
- `07-prd-mvp6-context-intelligence.md` — context router, role-aware context packs, token budgeting, adaptive escalation, token economics.
- `08-prd-mvp7-integrations-inference.md` — Forgejo/GitHub, MCP/tool integrations, inference gateway abstraction, 9Router/LiteLLM/direct providers/local models.
- `09-prd-mvp8-governance-scale.md` — RBAC, policy, secrets, audit, multi-project/multi-user scale, resilience, compliance, enterprise controls.
- `10-traceability-matrix.md` — roadmap and cross-MVP requirement traceability.
- `remote-agent-identities-and-sdlc.md` — remote agent identities, brokered authentication, and human-like SDLC collaboration on Forgejo and GitHub.

## Intended downstream consumers

Every PRD is structured for four specialist agent groups:

- **Architect** — system boundaries, APIs, service decomposition, lifecycle, scalability, deployment, failure domains.
- **Security** — trust boundaries, identity, secrets, sandbox isolation, policy, remote Git authority, audit, abuse cases.
- **Integration** — A2A, harness adapters, Git providers, MCP, CI/CD, model gateways, webhooks, external contracts.
- **Data Design** — domain entities, identifiers, state machines, events, persistence, derived intelligence, lineage, retention.

The PRDs intentionally define product behavior and constraints while avoiding premature lock-in to a specific implementation such as Graphify, Neo4j, 9Router, PostgreSQL, or a specific queue. Those are candidate technologies behind product interfaces unless explicitly elevated to a protocol requirement.
