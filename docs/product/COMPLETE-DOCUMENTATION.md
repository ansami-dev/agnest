# Complete Product Documentation Bundle


---

<!-- SOURCE: 00-README.md -->

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

## Source of truth and generated bundle

The split documents in this directory are the canonical product documentation. `COMPLETE-DOCUMENTATION.md` is a **generated bundle**: a concatenation of those documents produced and checked by `scripts/product_bundle.py`. It is **derived, not authoritative**. Where any other document cites the bundle, read the corresponding split document as the source of truth. Edit a split document, then regenerate the bundle; never edit the bundle by hand.

The ordered list of sources that make up the bundle — including this file — is declared in the machine-readable block below. `scripts/product_bundle.py` reads it for both `build` and `verify`, so the declared list is the single authority for bundle membership and order.

<!-- BUNDLE-SOURCES
00-README.md
01-product-vision.md
02-prd-mvp1-git-foundation.md
03-prd-mvp2-agent-runtime-fabric.md
04-prd-mvp3-orchestration-groups.md
05-prd-mvp4-review-quality-publish.md
06-prd-mvp5-repository-intelligence.md
07-prd-mvp6-context-intelligence.md
08-prd-mvp7-integrations-inference.md
09-prd-mvp8-governance-scale.md
10-traceability-matrix.md
remote-agent-identities-and-sdlc.md
-->

Rebuild the bundle after editing any split document, and verify it before committing:

```sh
python scripts/product_bundle.py build
python scripts/product_bundle.py verify
```

Both commands check the declaration before reading or writing anything. Every `*.md` directly under `docs/product` — except the generated bundle itself — must be declared; names must be plain filenames (no absolute, traversal, or separator-bearing paths), and the bundle may not declare itself. `verify` exits non-zero if a product document is present but undeclared, if a declared source is absent from the bundle, if the bundle contains a section with no declared source, or if any embedded section differs from its canonical file.

The regression tests cover unsafe declarations, an undeclared product document, and content drift:

```sh
python scripts/test_product_bundle.py
```

## Intended downstream consumers

Every PRD is structured for four specialist agent groups:

- **Architect** — system boundaries, APIs, service decomposition, lifecycle, scalability, deployment, failure domains.
- **Security** — trust boundaries, identity, secrets, sandbox isolation, policy, remote Git authority, audit, abuse cases.
- **Integration** — A2A, harness adapters, Git providers, MCP, CI/CD, model gateways, webhooks, external contracts.
- **Data Design** — domain entities, identifiers, state machines, events, persistence, derived intelligence, lineage, retention.

The PRDs intentionally define product behavior and constraints while avoiding premature lock-in to a specific implementation such as Graphify, Neo4j, 9Router, PostgreSQL, or a specific queue. Those are candidate technologies behind product interfaces unless explicitly elevated to a protocol requirement.

---

<!-- SOURCE: 01-product-vision.md -->

# Product Vision — Git-Native Multi-Agent Engineering Control Plane

## 1. Executive Summary

The product is a **Git-centric control plane for multi-agent software engineering**. It enables software teams and solo developers to operate heterogeneous AI coding agents as a coordinated engineering organization while preserving local Git control, sandbox isolation, reviewability, source-of-truth integrity, and explicit authority over remote repositories.

The platform is not another coding harness and is not a replacement for Hermes, Claude Code, Codex, OMP, or future agent runtimes. Instead, it provides a stable orchestration layer above them. An agent has a persistent identity, role, capabilities, memory references, permissions, task history, and group membership independent of the harness, model, and sandbox currently used to execute it.

The product addresses a structural problem in AI-assisted software development: frontier coding agents are capable, but today they often waste expensive context repeatedly rediscovering repository structure, operate in isolated sessions without durable team state, expose inconsistent runtime APIs, and are frequently granted broader Git and infrastructure permissions than necessary. Multi-agent systems make the problem worse because every additional agent repeats discovery and copies overlapping context.

The product solves this by combining four core ideas:

1. **Agent Fabric** — a harness-independent model for agents, capabilities, groups, tasks, delegation, artifacts, events, and approvals.
2. **Engineering Workspace** — local-first Git workspaces with isolated worktrees and sandboxed execution, reviewable before anything is pushed remotely.
3. **Context Intelligence** — repository-aware graph, lexical, semantic, and source retrieval that builds role-specific context packs instead of sending the whole repo.
4. **Governed Delivery** — quality gates, human approvals, remote Git authority separation, auditability, token/cost telemetry, and policy-driven publication.

The initial runtime focus is **Hermes, Claude Code, Codex, and OMP**. The MVP1 sandbox focus is **local Incus**, with a required system-container baseline and capability-gated OCI/VM modes; additional local or remote providers are demand-driven. The initial remote Git focus is **Forgejo and GitHub**. The protocol direction is **A2A for agent interoperability** and **MCP for tools/data access**, with adapters where runtimes do not natively implement those protocols.

The long-term outcome is a platform where a user can connect a repository and issue, assign work to a persistent AI engineering team, watch each specialist operate in an isolated local workspace, inspect source-level changes and review findings, measure how much context and cost was avoided, and approve the final commit/push/PR only when satisfied.

---

## 2. Product Thesis

### 2.1 Core thesis

AI coding agents should be treated as **engineering workers operating inside governed software delivery infrastructure**, not as isolated chat sessions with repository access.

A capable software engineering agent requires more than a model:

- persistent identity and role;
- a controlled workspace;
- task and dependency state;
- appropriate repository context;
- tools and external integrations;
- explicit authority boundaries;
- review and validation stages;
- durable artifacts and decisions;
- observability over actions, tokens, and costs.

The platform provides those missing layers while leaving the runtime interchangeable.

### 2.2 Context thesis

Large context windows are emergency capacity, not a target utilization level.

The platform should optimize for **minimum sufficient context**:

- retrieve only likely-relevant symbols, files, tests, specifications, and history;
- verify conclusions against source code before edits or decisions;
- escalate context breadth only when confidence is low or evidence conflicts;
- avoid duplicating the same context across agents when structured artifacts can be reused;
- expose context efficiency as a product metric.

### 2.3 Git thesis

Remote Git hosting is a collaboration and publication boundary, not the agent's primary workspace.

Agents should work locally in isolated worktrees and sandboxes. Diff review, tests, specialist review, and policy checks occur before remote publication. Git credentials for Forgejo/GitHub should normally remain in the control plane or dedicated Git service rather than inside agent sandboxes.

### 2.4 Multi-agent thesis

Multi-agent does not mean "many agents talking in a shared chat." The platform supports two distinct collaboration modes:

- **Deliberation** — several agents reason about the same problem and produce a decision, recommendation, or review artifact.
- **Workflow** — agents own different delivery stages and pass durable artifacts between them.

Free-form conversation remains useful, but durable system state must reside outside transcripts.

---

## 3. Vision Statement

> **Build the open control plane for Git-native AI software engineering teams: bring your agents, bring your models, bring your repository, and give every agent exactly the context and authority it needs—nothing more.**

Supporting tagline:

> **Give every agent the context it needs — and nothing it doesn't.**

---

## 4. Target Users

### 4.1 Solo AI-native developer

Runs multiple specialized agents and wants frontier-model quality without repeatedly paying for whole-repository context. Needs parallel work, isolated worktrees, local review, and flexible runtime choice.

### 4.2 AI engineering / platform team

Provides approved agent runtimes and sandbox templates to developers. Needs policy, observability, secrets isolation, reusable workflows, and centralized integration with Git/CI infrastructure.

### 4.3 Software engineering team lead

Delegates issues to AI implementation/review agents but requires human control before remote publication. Needs visibility into diffs, tests, findings, context, and cost.

### 4.4 Security / regulated engineering team

Requires least privilege, sandbox isolation, auditability, secret controls, deterministic publication boundaries, and evidence of who/what changed code using which model and context.

### 4.5 OSS maintainer

Wants agents to triage, implement, test, and review issues across many contributors while retaining transparent Git history and human approval.

---

## 5. Product Principles

### P1. Harness agnostic

`Agent != Harness`.

The first supported harnesses are Hermes, Claude Code, Codex, and OMP. Product-domain concepts must not depend on any one harness's session model or command format.

### P2. Sandbox agnostic

`Agent != Sandbox`.

MVP1 uses local Incus behind a common sandbox contract. Docker, other VM managers,
Kubernetes, remote machines, and future runtimes are demand-driven implementations of
that replaceable boundary rather than baseline commitments.

### P3. Model agnostic

`Agent != Model`.

An agent role may use different models according to task, policy, cost, availability, or provider quota.

### P4. Git native

Repository, commit SHA, branch, worktree, diff, stage, commit, publish, PR, merge status, and Git provenance are first-class data.

### P5. A2A native

A2A semantics are the canonical interoperability model for agent discovery, task assignment, messages, and artifacts. Non-native harnesses are exposed through adapters.

### P6. Artifact driven

Durable state is represented by typed artifacts, findings, decisions, approvals, diffs, test results, and task state—not only chat history.

### P7. Context efficient

Context retrieval and role-aware context routing are core product capabilities, not an optional optimization.

### P8. Source verified

Graph, embeddings, summaries, and memories are derived data. Actual Git source and selected repository artifacts remain canonical.

### P9. Local-first, remote-by-approval

Agents should normally operate without remote write authority. Remote push, PR creation, and merge use explicit control-plane authority and policy.

### P10. Human override always exists

The platform can automate strongly, but humans must be able to pause, inspect, reject, re-run, reassign, revert, and override workflows.

---

## 6. Product Pillars

### 6.1 Agent Fabric

Provides persistent agent identities, capabilities, roles, groups, task assignment, execution adapters, lifecycle state, and A2A interoperability.

Key concepts:

- Agent Identity
- Runtime Adapter
- Harness Session
- Capability
- Role
- Group
- Task
- Artifact
- Event
- Finding
- Decision
- Approval

### 6.2 Engineering Workspace

Provides isolated local Git working environments coupled to sandboxed compute.

Key concepts:

- Project
- Repository
- Workspace
- Worktree
- Branch
- Base Commit
- Sandbox
- Diff
- Stage
- Commit
- Publish
- Pull Request
- Test Run

### 6.3 Context Intelligence

Provides repository intelligence and context assembly.

Key concepts:

- AST/Symbol Index
- Code Relationship Graph
- Lexical/BM25/Full-Text Search
- Vector/Semantic Search
- Git History Index
- Specification/Issue Index
- Hybrid Retrieval
- Graph Expansion
- Reranking
- Source Retrieval
- Context Pack
- Token Budget
- Context Escalation

### 6.4 Governed Delivery

Provides security, quality, observability, approval, policy, and publication control.

Key concepts:

- RBAC
- Agent Permissions
- Sandbox Policy
- Tool Permissions
- Secret Scope
- Network Policy
- Quality Gate
- Review Gate
- Human Approval
- Audit Trail
- Token/Cost Telemetry
- Model/Harness Trace

---

## 7. Product Architecture Layers

### Layer 1 — Experience Layer

Human-facing web/desktop UI for projects, issues, tasks, agents, groups, conversations, workspaces, changes, review findings, approvals, token/cost dashboards, and activity timelines.

Expected capabilities:

- project navigation;
- issue/task board;
- agent/group roster;
- agent activity/session view;
- code change/diff viewer;
- staged/unstaged changes;
- test results;
- specialist review findings;
- publish/PR controls;
- context efficiency dashboard;
- audit/activity timeline.

### Layer 2 — Project & Git Layer

Owns repository mirrors, worktrees, branches, workspace state, local Git operations, remote synchronization, publish, and PR lifecycle.

### Layer 3 — Orchestration / Control Plane

Owns task state, workflow dependencies, events, delegation, approvals, retries, artifact handoff, scheduling, and group coordination.

### Layer 4 — Agent & Group Layer

Owns persistent agent identities, capabilities, permissions, role configuration, group membership, deliberation/workflow semantics, and execution policies.

### Layer 5 — Agent Interoperability Layer

Owns A2A-compatible agent surfaces and runtime adapters for Hermes, Claude Code, Codex, OMP, and future harnesses.

### Layer 6 — Workspace & Sandbox Layer

Owns sandbox lifecycle, execution, mounted workspace access, resource controls, health, snapshots where applicable, and environment policy.

### Layer 7 — Repository Intelligence Layer

Owns repository indexing and derived knowledge: source structure, symbols, relationships, code graph, lexical index, embeddings, Git history, test mapping, documentation/spec references.

### Layer 8 — Context Engine

Owns query classification, hybrid retrieval, role-aware selection, graph expansion, source verification, deduplication, token budgeting, adaptive escalation, and final context pack generation.

### Layer 9 — Inference Layer

Owns model/provider abstraction, routing, fallback, prompt caching, quota awareness, optional compression, and usage telemetry. Direct providers and gateways such as 9Router or LiteLLM are pluggable implementations.

### Layer 10 — Tool & Integration Layer

Owns Forgejo/GitHub, CI/CD, MCP servers, issue systems, artifact stores, documentation systems, browser/research, secrets managers, and external services.

### Layer 11 — Governance & Observability Layer

Cross-cuts every layer with identity, authorization, audit, secrets handling, policy, telemetry, tracing, cost accounting, and compliance evidence.

---

## 8. Core Domain Model

### Project

A logical software product or codebase context. May contain one or more repositories, agents, groups, workflows, and policy profiles.

### Repository

A Git repository with remote metadata, mirror/cache state, default branch, supported workflows, and repository intelligence state.

### Issue

Imported or locally-created engineering work item. Can originate from Forgejo/GitHub or future integrations.

### Task

An executable unit of work assigned to an agent or group. A task has lifecycle, owner, dependencies, inputs, artifacts, workspace references, context references, and outcome.

### Agent

Persistent identity independent from runtime. Stores role, capabilities, permissions, policy, history references, group memberships, and external identity bindings (e.g. Forgejo user account or GitHub App bot persona).

### Runtime Binding

Concrete execution binding for an agent, e.g. Hermes + local model, Claude Code + Claude model, Codex + GPT model, OMP + selected provider.

### Group

Collection of agents operating in deliberation or workflow mode with explicit coordination, context, artifact, and termination policies.

### Workspace

Task-scoped local Git worktree plus execution metadata. It is the primary engineering working state.

### Sandbox

Compute boundary hosting a harness/runtime and mounted/copy-on-write workspace.

### Artifact

Durable typed output such as architecture proposal, implementation report, review findings, security findings, test report, diff summary, decision, or handoff.

### Context Pack

Versioned set of evidence, source references, summaries, graph findings, issue data, and role-specific instructions assembled for a task execution.

### Approval

Human or policy gate for sensitive transitions such as commit, publish, PR, secret access, expanded network access, or merge.

---

## 9. Canonical End-to-End Workflow

1. User connects Forgejo/GitHub repository.
2. Control plane maintains or updates a local repository mirror.
3. Issue is imported or selected.
4. User or workflow assigns issue to an agent/group, and remote issue assignee is updated to reflect the agent's remote persona.
5. Control plane creates branch + worktree + workspace.
6. Sandbox provider provisions a local Incus instance in MVP1 and attaches the workspace; later providers remain behind the same product boundary.
7. Repository intelligence retrieves likely relevant code, tests, specs, and history.
8. Context engine produces a role-specific context pack.
9. Runtime adapter starts or resumes Hermes/Claude Code/Codex/OMP.
10. Agent performs work locally.
11. Workspace emits change events and test results.
12. Specialist agents review uncommitted or committed local diff.
13. Findings are returned as typed artifacts.
14. Implementer revises until quality gates pass.
15. Human inspects actual source diff in the product UI.
16. User approves commit and/or publish according to policy.
17. Git service commits/pushes using control-plane authority with author attribution to the implementer agent.
18. PR is created in Forgejo/GitHub authored by the implementer agent; specialist reviewer agents are assigned, posting native PR reviews and inline comments.
19. CI status is tracked and correlated to the task/workspace.
20. Workflow completes, workspace is retained or destroyed according to policy, and all actions remain auditable.

---

## 10. Group Semantics

### Deliberation Group

Designed for architecture, threat modeling, product reasoning, and difficult reviews.

Properties:

- coordinator optional;
- max rounds / token budget;
- mention or automatic activation;
- per-role context packs;
- structured disagreement and decision output;
- termination when consensus, coordinator decision, budget limit, or explicit stop condition is reached.

Example:

- Architect
- Security
- Integration
- Data Design

Output: `ArchitectureDecision` artifact plus unresolved questions.

### Workflow Group

Designed for delivery stages.

Example:

Product/Requirements → Architect → Implementer → QA → Code Review → Security → Publish Approval.

Properties:

- stage dependencies;
- completion criteria;
- retry/rework loop;
- artifact contracts between stages;
- approvals before selected transitions.

---

## 11. Repository Intelligence Vision

Repository intelligence must support both precise code lookup and broad structural reasoning.

### Deterministic structure

- files/directories;
- symbols;
- imports;
- calls where statically available;
- inheritance/implementation;
- language/module boundaries;
- tests and references;
- config/dependency files.

### Derived search

- lexical/BM25/full-text for exact identifiers, strings, APIs, errors, and configuration keys;
- vector/semantic retrieval for conceptual similarity;
- graph traversal for dependency and blast-radius reasoning;
- Git history for recency, change ownership, previous fixes, and regression clues.

### Source verification

The intelligence layer returns candidate scope and source references. Before editing, the runtime must retrieve actual source content. The product must preserve provenance from retrieval result to file/commit/line range where feasible.

### Workspace awareness

Repository intelligence must distinguish base repository state from active workspace state. Worktree changes should be indexed incrementally or represented as an overlay so reviewers reason about the current task, not stale `main`.

---

## 12. Context Intelligence Vision

The context engine is a product capability, not just an optimization library.

### Inputs

- issue/task;
- agent role/capabilities;
- workspace and current diff;
- repository intelligence;
- prior artifacts;
- applicable architecture/security/specification documents;
- recent test/review results;
- explicit user instructions.

### Pipeline

1. classify information need;
2. retrieve lexical candidates;
3. retrieve semantic candidates;
4. retrieve graph candidates;
5. fuse and rerank;
6. expand related nodes where useful;
7. load canonical source evidence;
8. deduplicate overlapping evidence;
9. enforce token budget;
10. generate versioned context pack;
11. escalate if runtime reports missing/ambiguous/conflicting context.

### Context policies

Role examples:

- Implementer: source, tests, API/data contracts, relevant issue requirements.
- QA: requirements, diff, test map, impacted behavior, historical regressions.
- Code Review: diff, callers/callees, conventions, relevant source, test impact.
- Security: trust boundaries, auth/secrets paths, sensitive dependencies, diff, security standards.
- Architect: module boundaries, dependency graph, ADRs, constraints, change blast radius.

### Token economics

The product should expose:

- estimated repository token footprint;
- retrieved candidate tokens;
- tokens after rerank/dedup;
- actual model input/output;
- prompt cache hits where available;
- compressed tokens where applicable;
- per-agent/per-task cost;
- avoided context ratio;
- quality outcome metrics such as tests/review pass rate.

The success goal is not maximum compression; it is **minimum sufficient context at acceptable quality**.

---

## 13. Security and Trust Vision

### Trust boundaries

The system must treat the following as separate trust zones:

- user/browser;
- control plane;
- Git credential service;
- runtime adapter;
- sandbox;
- repository workspace;
- external model/provider;
- MCP/tool server;
- remote Git provider;
- external CI/CD.

### Default authority model

Agent sandbox normally may:

- read assigned workspace;
- modify assigned workspace;
- execute configured commands/tests;
- use explicitly allowed network destinations/tools.

Agent sandbox normally may not:

- push remote Git;
- merge PRs;
- read arbitrary platform secrets;
- access other workspaces;
- access production systems;
- expand its own permissions.

Remote Git authority belongs to a dedicated control-plane integration with auditable policy gates.

### Secrets

- secrets are scoped by task/runtime/tool;
- avoid persistent plaintext credentials inside sandbox filesystem;
- short-lived credentials preferred;
- secret access produces audit events;
- inference API keys should be centrally managed where possible;
- runtime-specific credentials require isolated storage and explicit lifecycle.

---

## 14. Product Differentiation

The product is differentiated from generic agent frameworks by the combination of:

1. **Harness independence** — Hermes, Claude Code, Codex, OMP under one agent model.
2. **Git-native local-first workspaces** — source changes are first-class and reviewable before remote publication.
3. **Sandbox-provider abstraction** — local Incus first, with additional providers added by demonstrated demand rather than baked into product identity.
4. **Dual multi-agent semantics** — deliberation and workflow are distinct first-class modes.
5. **Artifact-driven coordination** — structured handoffs instead of transcript dependence.
6. **Repository intelligence** — graph + lexical + semantic + Git-aware retrieval.
7. **Context economics** — measurable minimization of frontier input/output tokens.
8. **Governed publication** — remote credentials and publication authority remain outside default agent sandbox.
9. **Source verification** — graph/RAG accelerates investigation but never silently replaces canonical code.

---

## 15. Non-Goals

The product is not intended to:

- replace Git itself;
- replace Forgejo/GitHub/GitLab as remote collaboration hosts;
- become a new proprietary coding harness;
- force a single model provider;
- force a single graph/vector database;
- allow opaque autonomous production deployment without policy;
- treat generated summaries as canonical source;
- optimize solely for benchmark token reduction at the expense of engineering correctness.

---

## 16. Roadmap and MVP Sequence

### MVP 1 — Git Foundation & Sandboxed Workspaces

Establish projects, repositories, local mirrors, branches, worktrees, sandbox providers, workspace lifecycle, local diff, tests, and no-remote-write default.

**Proof:** an issue can obtain an isolated workspace and sandbox, produce local changes, and be inspected without any remote write.

### MVP 2 — Agent Runtime Fabric

Introduce persistent agent identity, runtime bindings, A2A-compatible adapter layer, and first support for Hermes, Claude Code, Codex, and OMP.

**Proof:** the same logical agent can execute a task through different harnesses without changing project/task semantics.

### MVP 3 — Multi-Agent Orchestration & Groups

Introduce tasks, events, artifacts, approvals, dependencies, deliberation groups, workflow groups, retries, and structured handoffs.

**Proof:** multiple heterogeneous agents can collaborate on one engineering issue with durable state outside chat transcripts.

### MVP 4 — Review, Quality Gates & Controlled Publish

Introduce diff UI, hunk-level review, QA/code/security review loops, test gates, local commit, publish approval, Forgejo/GitHub push, and PR creation.

**Proof:** an issue can move from implementation through specialist reviews to an approved PR without granting agent sandbox direct remote-write credentials.

### MVP 5 — Repository Intelligence

Introduce deterministic code indexing, symbol/dependency graph, lexical search, semantic retrieval, Git history enrichment, workspace overlay, impact analysis, and source provenance.

**Proof:** agents can identify likely implementation/review scope with fewer repository exploration steps while still reading canonical source before edits.

### MVP 6 — Context Intelligence & Token Economics

Introduce hybrid retrieval orchestration, role-aware context packs, context budgeting, deduplication, adaptive escalation, reusable structured artifacts, and token/cost dashboards.

**Proof:** on benchmark issues, the platform materially reduces frontier-model input tokens while preserving engineering quality metrics.

### MVP 7 — Integrations & Inference Fabric

Expand Forgejo/GitHub/CI/MCP/tool integrations and introduce inference gateway abstraction supporting direct providers, 9Router, LiteLLM, CLIProxyAPI/OpenAI-compatible endpoints, and local models.

**Proof:** agents can select models/providers and tools by policy without coupling application workflow to a single vendor.

### MVP 8 — Governance, Enterprise Security & Scale

Add multi-user RBAC, organizations/projects, policy engine, secret broker, network controls, stronger audit/compliance, HA/resilience, quotas, retention, cross-project administration, and enterprise observability.

**Proof:** multiple teams can operate governed agent workflows with enforceable least privilege, auditable publication, and controlled infrastructure/model spend.

---

## 17. Success Metrics

### Engineering outcome

- task completion rate;
- percentage of tasks passing automated tests after first implementation cycle;
- reviewer finding rate and rework loops;
- regression rate after merge;
- median issue-to-PR time.

### Context efficiency

- median frontier input tokens per issue;
- percentage reduction versus baseline harness-only workflow;
- percentage of context retrieved but not sent;
- cache hit rate where provider supports caching;
- context escalation frequency;
- retrieval precision/recall proxies based on final files changed and review findings.

### Agent orchestration

- task handoff success rate;
- retries caused by adapter/runtime failures;
- average artifact size vs conversation size;
- number of unnecessary agent turns avoided;
- workflow completion without manual recovery.

### Security/governance

- remote pushes with explicit approval/policy evidence;
- unauthorized secret/tool/network attempts blocked;
- sandbox escape or cross-workspace access incidents;
- audit completeness;
- percentage of production-impacting actions with traceable actor/runtime/model/context.

### Platform reliability

- sandbox provisioning success;
- runtime adapter success;
- repository mirror/worktree operation reliability;
- event processing latency;
- mean time to recover stuck tasks.

---

## 18. Product UX Vision

The primary workspace should place human intent, agent activity, and actual Git state side by side.

Suggested desktop/web structure:

- left: projects, issues, tasks, agents, groups, workspaces;
- center: selected agent/group activity, structured artifacts, current task timeline;
- right: workspace state, changed files, diff, tests, review findings, impact analysis, publish controls.

Users must be able to inspect what changed without trusting an agent summary. The UI should make local vs remote state explicit, e.g. `Uncommitted`, `Committed locally`, `Not published`, `Published`, `PR open`.

---

## 19. Open Product Questions

1. Should agent memory be platform-native, harness-native, or both with scoped synchronization?
2. Which parts of A2A should be mandatory in the internal contract versus adapter implementation detail?
3. How should workspace graph overlays be represented across simultaneous worktrees?
4. Should context packs be persisted for complete reproducibility or regenerated from references plus hashes?
5. What level of runtime transcript should be retained by default given privacy/cost/diagnostic tradeoffs?
6. Which Git actions require human approval by default: commit, publish, PR, merge?
7. How should local repository mirrors be shared safely across users/projects?
8. How should token efficiency be benchmarked against engineering quality to prevent misleading optimization?
9. How much model-specific prompt logic belongs in the platform versus runtime adapters?
10. What demonstrated demand and portability evidence should trigger an additional local or remote sandbox-provider implementation?

---

## 20. Product Constitution

The project should reject design changes that violate these defaults without an explicit ADR:

- Agent identity must not be coupled to a single harness.
- Task/workflow state must not live only in chat transcripts.
- Repository source must remain canonical over derived intelligence.
- Agent sandbox must not receive broad remote Git authority by default.
- Sandbox backend must remain replaceable.
- Model/provider must remain replaceable.
- Context optimization must never silently remove the ability to retrieve canonical source.
- Security and audit are product behavior, not late enterprise add-ons.
- Local changes must remain reviewable before publication.
- Token savings must be evaluated together with correctness and review outcomes.

---

<!-- SOURCE: 02-prd-mvp1-git-foundation.md -->

# PRD — MVP 1: Git Foundation & Sandboxed Workspaces

## 1. Purpose

Establish the local-first engineering substrate: projects, repositories, local mirrors, task workspaces, Git worktrees, sandbox lifecycle, test execution, and inspectable local diffs. This MVP intentionally avoids multi-agent orchestration complexity; it proves that the platform can create a safe, isolated place where future agents will work without granting remote-write authority.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Create and manage Projects and Git Repositories.
- Connect Forgejo/GitHub repositories for read/fetch operations.
- Maintain local repository mirror/cache and create isolated task worktrees.
- Provision a sandbox through a provider abstraction implemented in MVP1 by Incus on the local Agnest appliance VM.
- Mount or expose the assigned workspace to the sandbox.
- Execute commands and tests inside the sandbox.
- Track local changes, staged state, base commit, branch, and workspace status.
- Allow human inspection of local diff before any remote action.
- Enforce no remote Git write from sandbox by default.

## 4. Non-Goals

- Agent identity and A2A runtime adapters.
- Multi-agent groups or delegation.
- Repository graph/vector intelligence.
- Automatic PR creation or merge.
- Organization-wide RBAC beyond a minimal local admin/operator model.
- Advanced model routing.
- Remote sandbox providers, remote workers, and Workspace replication between hosts.
- Docker and Proxmox sandbox adapters; these require demonstrated demand and a later decision.

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Connect repository
1. User creates a Project.
2. User provides Forgejo/GitHub repository reference and authorized integration.
3. Platform fetches repository into a controlled mirror/cache.
4. Platform records default branch and latest fetched commit.

### W2 — Create task workspace
1. User selects repository and task/issue identifier.
2. Platform creates branch name according to configurable convention.
3. Platform creates isolated worktree from a specific base commit.
4. Platform provisions sandbox and attaches workspace.
5. User can open workspace status before execution.

### W3 — Execute work locally
1. Command is executed in sandbox.
2. Files are modified only inside assigned workspace.
3. Platform continuously/periodically updates Git status.
4. Tests can be executed and persisted as TestRun records.

### W4 — Inspect and discard
1. User views changed files and unified/side-by-side diff.
2. User can discard the entire workspace or revert selected files/hunks where supported.
3. No remote branch is created unless later explicitly published.

## 7. Functional Requirements

- **FR-M1-001 Project CRUD:** create/read/update/archive projects.
- **FR-M1-002 Repository connection:** register Forgejo/GitHub remote, default branch, integration identity, fetch state.
- **FR-M1-003 Repository mirror/cache:** maintain a local Git object store suitable for efficient worktree creation.
- **FR-M1-004 Base commit pinning:** every workspace records exact base commit SHA.
- **FR-M1-005 Workspace creation:** create unique workspace ID, branch, worktree path, repository link, status.
- **FR-M1-006 Sandbox provider interface:** support create/start/stop/exec/mount-or-workspace-bind/health/destroy.
- **FR-M1-007 Local Incus provider:** provision task Sandboxes through an Incus daemon local to the Agnest appliance VM using server-owned image/resource/network profiles.
- **FR-M1-008 Incus container modes:** system container is the required baseline; OCI application container is enabled only when its required capabilities are positively evidenced.
- **FR-M1-009 Incus VM capability:** Incus VM uses the same logical lifecycle when nested virtualization and required capabilities are available; VM support is optional for an otherwise healthy MVP1 installation.
- **FR-M1-010 Workspace confinement:** sandbox filesystem write access is limited to assigned workspace plus explicitly configured ephemeral paths.
- **FR-M1-011 Command execution:** run shell command with stdout/stderr/exit code/timestamps and timeout.
- **FR-M1-012 Test run:** execute named test command and persist result.
- **FR-M1-013 Git status:** report modified, added, deleted, renamed, staged, untracked files.
- **FR-M1-014 Diff retrieval:** show file and hunk-level diff against base/HEAD.
- **FR-M1-015 Stage/unstage/revert:** expose safe local Git operations through workspace service.
- **FR-M1-016 Workspace lifecycle:** states at minimum `CREATING`, `READY`, `ACTIVE`, `DIRTY`, `FAILED`, `STOPPED`, `DISCARDED`, `ARCHIVED`.
- **FR-M1-017 Remote-write prohibition:** sandbox does not receive remote push credential by default.
- **FR-M1-018 Fetch/update control:** base repository can fetch remote updates without mutating active worktree unexpectedly.
- **FR-M1-019 Concurrent workspace isolation:** multiple workspaces from same repository can operate concurrently without sharing working tree state.
- **FR-M1-020 Local-only operation marker:** UI/API clearly indicates workspace has not been published remotely.

## 8. Non-Functional Requirements

- Workspace creation target: <= 15 seconds for warm local mirror excluding sandbox cold-boot variability.
- All Git state transitions must be idempotent or return a recoverable conflict state.
- Workspace operations must tolerate process restart without losing canonical Git state.
- Sandbox resource limits must be configurable.
- File paths must be normalized and protected against path traversal.
- The system must support repositories substantially larger than a single task's working set without loading complete contents into application memory.
- Destructive Git operations require explicit API intent and audit entry.

## 9. Domain Entities and Data Considerations

Core entities: `Project`, `Repository`, `RepositoryRemote`, `RepositoryFetchState`, `Workspace`, `WorkspaceBranch`, `Sandbox`, `SandboxProvider`, `CommandRun`, `TestRun`, `WorkspaceChangeSummary`.

Important identifiers: immutable internal UUID plus external Git identifiers; commit SHA is canonical for source version. Workspace must reference both intended base branch and pinned base SHA. Sandbox IDs are provider-scoped and must not become stable product identity.

Persist state machine transitions and timestamps. Large command logs/diffs may require artifact/blob storage rather than database rows. Store hashes/metadata to detect stale diff/test results after source changes.

## 10. Integration Requirements

- Forgejo and GitHub: repository metadata and fetch authentication.
- Native Git CLI/libgit operations: clone/mirror/fetch/worktree/status/diff/add/reset/restore.
- Local Incus daemon/API through broker-owned access.
- Incus system-container support; optional OCI application-container and VM capabilities are discovered rather than assumed.
- Remote Incus, Docker, Proxmox, and other provider contracts are deferred until demonstrated demand.

Integration credentials must be controlled by the platform, not copied into the sandbox unless explicitly required for read-only dependency access.

## 11. Security and Trust Requirements

- Define trust boundary between control plane, Git service, sandbox host, and task sandbox.
- Sandbox must not inherit control-plane environment secrets.
- Remote Git write credential must not exist in default sandbox.
- Network access must be policy-configurable; default profile should be narrower than unrestricted host networking.
- Workspace mount must prevent access to sibling workspaces and repository integration secrets.
- Command execution must have timeout, output bounds, and cancellation.
- Audit all workspace create/destroy, command execution metadata, Git staging/revert operations, and credentialed fetch.
- Threat model symlink/path traversal and malicious repository content.

## 12. Architecture Considerations and Constraints

- Separate logical `GitWorkspaceService` from sandbox provider.
- Prefer a local bare mirror/object cache plus per-task worktrees to avoid repeated full clones.
- Do not couple workspace path semantics to a specific sandbox backend.
- Git operations that affect remote state are explicitly out of sandbox responsibility.
- Provider-specific capabilities should be declared, not hidden behind a falsely uniform abstraction.
- Define recovery for orphaned worktrees/sandboxes after control-plane restart.
- Treat Git repository as source of truth for file state; database stores orchestration metadata.

## 13. Observability and Telemetry

Capture: workspace provisioning latency, sandbox provisioning latency, command duration/exit code, test status, files changed, diff size, workspace lifecycle transitions, provider errors, Git operation failures, orphan cleanup count.

Every action must correlate `project_id`, `repository_id`, `workspace_id`, and later `task_id` even if task orchestration is minimal in MVP1.

## 14. Acceptance Criteria

- Connect a Forgejo repository and fetch default branch.
- Create two concurrent workspaces from the same base SHA without file-state interference.
- Start a local Incus system-container Workspace, modify files, run a test, inspect diff, then discard without remote changes.
- Demonstrate that unsupported Incus OCI/VM capabilities are reported explicitly and do not make the required system-container baseline unhealthy.
- Demonstrate sandbox lacks remote push credential and a direct `git push` fails by default.
- Restart control-plane service and recover workspace metadata/status.
- Revert a selected file and confirm diff/test metadata becomes stale/recomputed appropriately.
- Destroy sandbox while preserving or archiving workspace according to user choice.

## 15. Dependencies

External: Git, Forgejo/GitHub connectivity, and local Incus host capability.
Internal: base authentication/configuration, artifact/log storage, foundational API/UI shell.

## 16. Risks and Mitigations

- **Worktree corruption:** use pinned base SHAs, controlled Git service, cleanup/reconciliation.
- **Sandbox/provider behavior mismatch:** capability discovery and provider conformance tests.
- **Credential leakage:** central credential service, environment allowlist, mount review.
- **Repository storage growth:** shared object store, garbage-collection policy, workspace retention.
- **Malicious repo scripts:** restricted default network/privilege and explicit execution policy.

## 17. Open Questions

1. Is local bare mirror per repository or shared object cache across forks preferred?
2. What is the default workspace retention after completion/failure?
3. Should stage/unstage be implemented via Git CLI exclusively or library abstraction?
4. How should Windows-hosted sandboxes fit the provider contract later?
5. Which network policy should be default for dependency installation?

## 18. Handoff — Architect Agent

Produce an architecture proposal covering service boundaries for Project/Repository/Workspace/Sandbox, provider interfaces, repository mirror strategy, worktree lifecycle, recovery of orphaned resources, API contracts, event model, concurrency model, and deployment topology. Explicitly document which state is canonical in Git vs database and provide failure-state diagrams.

## 19. Handoff — Security Agent

Produce threat model and trust-boundary diagram. Specify the local Incus system-container isolation baseline, capability-gated OCI/VM differences, required Linux capabilities restrictions, mount rules, network policy, secret-handling rules, remote Git credential separation, malicious-repository threats, command execution controls, and audit requirements. Define minimum security conformance tests for each enabled Incus instance kind.

## 20. Handoff — Integration Agent

Specify Forgejo/GitHub repository connection flows, Git credential handling, Git fetch semantics, the local Incus provider contract, instance-kind capability discovery, error normalization, and health checks/timeouts. Do not invent remote-provider or Workspace-transfer semantics before a later demand-driven decision.

## 21. Handoff — Data Design Agent

Define schemas/state machines for Project, Repository, Remote, Workspace, Sandbox, CommandRun, TestRun, and ChangeSummary. Define immutable vs mutable fields, unique constraints, commit-SHA lineage, lifecycle transition history, large-log/diff storage strategy, retention, and stale-result invalidation rules.

---

<!-- SOURCE: 03-prd-mvp2-agent-runtime-fabric.md -->

# PRD — MVP 2: Agent Runtime Fabric

## 1. Purpose

Introduce persistent agent identity and a harness-neutral execution model. The platform must run Hermes, Claude Code, Codex, and OMP through runtime adapters while presenting a consistent task/session/artifact interface to the control plane. A2A semantics become the interoperability contract even where a harness requires a translation adapter.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Create persistent Agent identities independent of harness, model, and sandbox.
- Define runtime adapter contract and A2A-compatible external/internal agent surface.
- Support Hermes, Claude Code, Codex, and OMP as the first four harnesses.
- Bind an Agent to a Workspace/Sandbox for execution without making the binding permanent.
- Normalize runtime lifecycle, streaming output, tool/activity events, cancellation, completion, and structured artifacts.
- Preserve harness-specific capability differences through explicit capability advertisement.
- Allow same Agent identity to switch harness/model between tasks while retaining role/history references.

## 4. Non-Goals

- Multi-agent group orchestration.
- Automated cross-agent delegation.
- Advanced long-term memory synchronization between harnesses.
- Complex model routing policies.
- Repository intelligence/context minimization beyond basic file/task context.

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Register agent
User creates `Hephaestus`, assigns role `Implementation`, capabilities, default runtime preferences, and permissions.

### W2 — Bind runtime
For a selected task/workspace, platform chooses or user selects `Claude Code`, `Codex`, `Hermes`, or `OMP`, provisions required runtime inside sandbox, and establishes adapter session.

### W3 — Execute task
Control plane sends normalized task instruction plus context references. Adapter translates to harness-specific invocation. Runtime streams activity and returns completion plus artifacts.

### W4 — Rebind same identity
A later task runs `Hephaestus` through a different harness while preserving agent identity, role, history, and policies.

## 7. Functional Requirements

- **FR-M2-001 Agent CRUD:** persistent identity, display name, role, description, capability tags, policy profile.
- **FR-M2-002 RuntimeAdapter interface:** initialize, capability discovery, start/resume session, send task/message, stream events, cancel, collect artifacts, shutdown.
- **FR-M2-003 RuntimeBinding:** bind agent + harness + model/provider configuration + sandbox + workspace + task.
- **FR-M2-004 Harness capability model:** declare file editing, shell, tool calling, MCP, native A2A, streaming, approvals, subagents, model selection, resume support.
- **FR-M2-005 A2A Agent Card surface:** expose normalized identity/capabilities for routable agents where applicable.
- **FR-M2-006 A2A task semantics:** normalized task ID, state, message parts, artifact references, progress, cancellation.
- **FR-M2-007 Hermes adapter:** start/resume selected Hermes profile/bot/runtime and normalize outputs.
- **FR-M2-008 Claude Code adapter:** launch or connect CLI/runtime session in assigned sandbox/workspace.
- **FR-M2-009 Codex adapter:** launch/connect Codex runtime with assigned workspace and configured model/provider.
- **FR-M2-010 OMP adapter:** launch/connect OMP runtime and normalize tool/activity outputs.
- **FR-M2-011 Streaming:** adapter emits normalized activity events without requiring control plane to parse raw terminal text where structured hooks exist.
- **FR-M2-012 Cancellation:** task execution can be cancelled and sandbox/process cleanup is deterministic.
- **FR-M2-013 Structured artifacts:** runtime can emit implementation summary, changed-file list, test summary, questions, findings, or generic artifact references.
- **FR-M2-014 Harness transcript retention policy:** configurable raw transcript retention separate from canonical task/artifact state.
- **FR-M2-015 Runtime health:** adapters expose availability/version/auth/capability diagnostics.
- **FR-M2-016 Identity portability:** changing runtime must not create a new Agent record.
- **FR-M2-017 Model metadata:** record actual model/provider used when knowable without hard-coding product logic to it.
- **FR-M2-018 Runtime environment requirements:** adapter declares required binaries, env vars, filesystem paths, and network access.
- **FR-M2-019 External identity binding:** bind persistent agent identity to provider-specific remote persona (Forgejo user account, GitHub App bot) and secret references.

## 8. Non-Functional Requirements

- Adapter failure must not corrupt workspace.
- Runtime-specific errors must map to normalized error classes while preserving raw diagnostic detail.
- Adapter startup should be retryable and idempotent where safe.
- Control plane must remain responsive if runtime streams large output.
- Raw stdout/stderr must have bounded buffering/backpressure.
- Runtime capability detection must be version-aware.
- A single adapter crash must not bring down unrelated task executions.

## 9. Domain Entities and Data Considerations

Entities: `Agent`, `AgentRole`, `Capability`, `RuntimeAdapterType`, `RuntimeBinding`, `RuntimeSession`, `RuntimeCapabilitySnapshot`, `AgentExecution`, `RuntimeEvent`, `ArtifactReference`, `ModelExecutionMetadata`, `ExternalAgentIdentity`.

Agent identity is long-lived. RuntimeBinding is task/session scoped. RuntimeSession may be resumable but must not become the durable source of task state. Store adapter version and capability snapshot for reproducibility.

## 10. Integration Requirements

- A2A protocol semantics for discovery/task/artifact interoperability.
- Hermes runtime/profile/bot control surface.
- Claude Code CLI/runtime integration.
- Codex runtime integration.
- OMP runtime integration.
- Sandbox execution API from MVP1.
- Optional MCP configuration pass-through where harness supports it.

Adapters must clearly separate mandatory product contract from best-effort harness-specific features.

## 11. Security and Trust Requirements

- Runtime credentials and provider tokens must be scoped to the adapter execution and not exposed to unrelated agents/workspaces.
- Agent permissions constrain adapter actions even if harness itself is capable of more.
- Raw runtime requests/responses may contain source code or secrets; define logging/redaction defaults.
- Runtime adapter must not bypass workspace confinement.
- Validate runtime command construction against argument injection.
- Support kill/cancel of runaway runtime processes.
- Track which agent identity, runtime, model/provider, sandbox, and workspace produced every artifact/change.

## 12. Architecture Considerations and Constraints

- Runtime Adapter is an anti-corruption layer between product domain and harness-specific session semantics.
- Do not force all harnesses into identical capabilities; expose capability matrix and graceful degradation.
- Decide whether adapters run in control plane, sidecar, or inside sandbox; preferred design should minimize trusted computing base.
- A2A should be represented as a stable contract without assuming every harness natively implements it.
- Preserve runtime events as typed events when possible, raw text only as fallback.
- Separate logical Agent from runtime session lifecycle.

## 13. Observability and Telemetry

Capture adapter startup latency, session duration, runtime version, task completion state, cancellation latency, event volume, token usage if exposed, model/provider, adapter errors, process exits, retries, and artifact counts. Correlate all events with `agent_id`, `execution_id`, `runtime_binding_id`, `workspace_id`, `task_id`.

## 14. Acceptance Criteria

- Create one logical agent and run task A through Claude Code and task B through Codex without changing agent identity.
- Run equivalent task through Hermes and OMP adapters.
- Display capability differences for all four harnesses.
- Cancel an in-progress task and confirm process/session cleanup while workspace remains inspectable.
- Record actual runtime/harness/model metadata with produced changes.
- Resume a harness session where supported and explicitly report unsupported resume where not.
- Demonstrate agent runtime lacks access outside assigned workspace.
- Expose normalized task progress/artifact events to the UI/API.

## 15. Dependencies

MVP1 workspace/sandbox service; supported harness installations/licenses/auth; A2A schema/library selection; foundational event transport.

## 16. Risks and Mitigations

- **Harness CLI churn:** versioned adapters and compatibility test matrix.
- **False abstraction:** capability discovery and feature flags rather than lowest-common-denominator design.
- **Credential sprawl:** central secret references and runtime-scoped injection.
- **Unstructured output:** prefer hooks/protocols; robust fallback parser isolated per adapter.
- **Session state loss:** task/artifacts canonical in platform, not harness transcript.

## 17. Open Questions

1. Should adapters run inside the sandbox as sidecars or be managed externally?
2. How much harness-native memory should be synchronized to platform agent memory later?
3. Which A2A version/features are mandatory for the product contract?
4. What is the fallback when runtime cannot emit structured events?
5. How should runtime-specific approval prompts be bridged to platform approvals?

## 18. Handoff — Architect Agent

Define Runtime Adapter architecture, A2A boundary, process placement, adapter lifecycle, capability model, normalized execution state machine, event contracts, failure isolation, and sequence diagrams for start/send/cancel/resume. Provide an extension guide for a fifth harness without control-plane changes.

## 19. Handoff — Security Agent

Threat-model runtime adapters and provider credentials. Define per-agent permission enforcement, secret injection/removal, transcript redaction, process isolation, command construction safety, trust implications of harness auto-updaters/plugins, and how runtime-initiated approval requests map to platform gates.

## 20. Handoff — Integration Agent

Produce concrete integration contracts and compatibility matrices for Hermes, Claude Code, Codex, and OMP. Document installation/runtime prerequisites, authentication, model configuration, session resume behavior, streaming mechanisms, tool/MCP hooks, error taxonomy, and version testing strategy. Map native capabilities to normalized A2A/task/artifact concepts.

## 21. Handoff — Data Design Agent

Define Agent vs RuntimeBinding vs RuntimeSession vs Execution schemas and lifecycle. Specify capability representation/versioning, runtime metadata, event persistence, transcript retention, artifact references, model usage fields, and identity/history relationships that survive harness changes.

---

<!-- SOURCE: 04-prd-mvp3-orchestration-groups.md -->

# PRD — MVP 3: Multi-Agent Orchestration & Groups

## 1. Purpose

Turn independent agents into a coordinated engineering team. Introduce first-class tasks, dependencies, events, artifacts, approvals, findings, decisions, group membership, deliberation mode, workflow mode, retries, and structured handoffs. Durable coordination state must live outside conversational transcripts.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Model Task, Artifact, Event, Finding, Decision, Approval, and Dependency as first-class objects.
- Support agent-to-agent and user-to-agent task assignment through normalized A2A semantics.
- Provide Deliberation Groups for multi-agent reasoning on the same problem.
- Provide Workflow Groups for staged engineering delivery.
- Support coordinator, activation, turn, context, artifact, retry, and termination policies.
- Prefer structured artifact handoff over unnecessary conversational acknowledgements.
- Support rework loops and approval gates.
- Make workflow state visible and recoverable after service restart.

## 4. Non-Goals

- Full visual workflow builder/DSL.
- Complex enterprise organization hierarchy.
- Repository intelligence/context optimization beyond simple attached context.
- Remote publish/PR controls (MVP4).
- Autonomous merge or deployment.

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Deliberation
User assigns architecture question to group `Architecture` containing Architect, Security, Integration, Data Design. Each member receives role instruction, contributes findings, and coordinator produces `ArchitectureDecision` with unresolved questions.

### W2 — Delivery workflow
Implementation task passes through `Implementer → QA → Code Review → Security`. Failed review emits Finding artifact and returns task to implementation. Passed stages progress without requiring conversational acknowledgment.

### W3 — Approval gate
Security finding marked high severity blocks workflow until user explicitly accepts risk or implementation resolves it.

### W4 — Recovery
Control plane restarts mid-workflow; tasks/events/artifacts reconstruct current state and execution resumes safely.

## 7. Functional Requirements

- **FR-M3-001 Task entity:** title, objective, assignee, status, priority, parent, dependencies, inputs, outputs, workspace, timestamps.
- **FR-M3-002 Task state machine:** at minimum `QUEUED`, `READY`, `RUNNING`, `BLOCKED`, `WAITING_APPROVAL`, `COMPLETED`, `FAILED`, `CANCELLED`.
- **FR-M3-003 Dependency graph:** task starts only when prerequisite conditions satisfy policy.
- **FR-M3-004 Artifact types:** generic plus decision, finding, review, test, handoff, implementation summary.
- **FR-M3-005 Event bus:** typed task/agent/workspace/artifact/approval events with correlation IDs.
- **FR-M3-006 Approval:** human/policy approval request with subject, action, risk/context, decision, actor, timestamp.
- **FR-M3-007 Group CRUD:** members, coordinator, mode, policies.
- **FR-M3-008 Deliberation mode:** configurable rounds/budget/activation/termination and structured final synthesis.
- **FR-M3-009 Workflow mode:** ordered/DAG stages, completion criteria, retry/rework transitions.
- **FR-M3-010 Agent mention/direct message:** support targeted agent interaction without broadcasting full history to all members.
- **FR-M3-011 Structured handoff:** task completion can emit artifact references consumed by next stage.
- **FR-M3-012 Silence/no-op:** agents may explicitly produce no contribution without forcing a generated acknowledgment.
- **FR-M3-013 Retry:** configurable retry count/backoff/reassignment for runtime failures distinct from domain rejection.
- **FR-M3-014 Rework loop:** findings can reopen prior stage with traceable linkage.
- **FR-M3-015 Group context policy:** define which prior artifacts/messages are visible to each member.
- **FR-M3-016 Termination policy:** consensus, coordinator decision, max rounds, token/time budget, all-pass, or explicit human stop.
- **FR-M3-017 Workflow templates:** save/reuse group/workflow definitions.
- **FR-M3-018 Activity timeline:** reconstruct significant state from events/artifacts rather than raw transcript.
- **FR-M3-019 Manual override:** pause, resume, skip with reason, reassign, cancel.
- **FR-M3-020 Concurrency control:** prevent duplicate execution of same exclusive task stage.
- **FR-M3-021 Bi-directional deliberation synchronization:** project deliberation group round positions to remote issue comments, and ingest authorized human comments from remote Git hosts as priority human instructions into the next round context pack.


## 8. Non-Functional Requirements

- Event processing must be idempotent.
- Orchestration state must survive restart.
- Workflow engine must distinguish infrastructure/runtime failures from review/domain failures.
- The platform must prevent infinite agent loops through explicit budgets/termination.
- Task and artifact APIs must support later distributed execution.
- Group execution should support parallel members when dependencies allow.

## 9. Domain Entities and Data Considerations

Entities: `Task`, `TaskDependency`, `TaskAssignment`, `Group`, `GroupMember`, `GroupPolicy`, `WorkflowTemplate`, `WorkflowRun`, `WorkflowStage`, `Artifact`, `ArtifactVersion`, `Finding`, `Decision`, `ApprovalRequest`, `ApprovalDecision`, `Event`, `RetryAttempt`, `Handoff`.

Artifacts must be immutable/versioned or explicitly superseded. Findings require severity/status/subject references. Events need globally unique IDs, causation/correlation IDs, actor, timestamp, and payload version.

## 10. Integration Requirements

- Runtime Fabric from MVP2.
- Workspace lifecycle from MVP1.
- A2A task/message/artifact semantics.
- Notification/UI event stream.
- Optional webhook/event integration foundation for later Forgejo/CI events.

## 11. Security and Trust Requirements

- Enforce permissions at task assignment and group invocation.
- Approval decisions must be authenticated, immutable, and auditable.
- Prevent a lower-trust agent from self-approving protected actions.
- Artifact visibility may be role/project scoped.
- Treat agent-generated instructions/artifacts as untrusted input to other agents; guard prompt/tool injection through context policy and source labeling.
- Group loops must have resource budgets to prevent uncontrolled spend.
- Manual override actions require actor/reason audit.

## 12. Architecture Considerations and Constraints

- Prefer event-driven orchestration with durable state over in-memory chat loops.
- Keep conversation service separate from workflow/task state.
- Group engine should compose Task/Artifact/Event primitives rather than implement a separate hidden state model.
- Support synchronous-looking UX over asynchronous/distributed execution.
- Define clear coordinator responsibilities; coordinator is a role/policy, not necessarily a permanent special agent.
- Artifact schemas should be extensible and versioned.

## 13. Observability and Telemetry

Capture task queue/run/block durations, group rounds, agent turns, retries, rework loops, approval wait time, event processing failures, artifact sizes, workflow completion rate, runtime vs domain failure counts, and manual overrides. Correlate causation across nested tasks.

## 14. Acceptance Criteria

- Create deliberation group with four agents and produce one versioned decision artifact with individual findings and unresolved questions.
- Create workflow group Implementer→QA→Code Review→Security and run through successful completion.
- Force QA failure and verify finding returns workflow to implementation while preserving history.
- Require human approval before a protected transition and block until decision.
- Restart orchestrator mid-run and recover exact workflow state without duplicate stage execution.
- Demonstrate agents do not all receive full raw transcript by default; next stage can consume structured artifacts.
- Cancel a group execution and terminate active runtime sessions safely.

## 15. Dependencies

MVP2 Agent Runtime Fabric, MVP1 workspace state, event persistence/transport, basic user authentication.

## 16. Risks and Mitigations

- **Agent loop/cost explosion:** round/time/token budgets and termination rules.
- **Duplicate execution:** idempotency keys and task leases.
- **Artifact schema sprawl:** versioned core schema plus typed extension registry.
- **Workflow deadlocks:** dependency validation and operator diagnostics.
- **Prompt injection across agents:** labeled provenance, context filtering, least privilege, source verification.

## 17. Open Questions

1. Should workflow definition be YAML/JSON initially or API-only?
2. How should consensus be represented in deliberation mode?
3. Which artifact types are canonical core vs plugin-defined?
4. Are group conversations retained fully by default or summarized/expired?
5. How should nested groups/subtasks affect budgets and termination?

## 18. Handoff — Architect Agent

Design task/workflow/event architecture, durable state machine, event delivery semantics, task leasing/idempotency, deliberation coordinator model, workflow DAG execution, recovery, artifact versioning interfaces, and future distributed scheduler compatibility. Provide sequence diagrams for rework and approval.

## 19. Handoff — Security Agent

Define authorization for task assignment, group invocation, artifact visibility, manual overrides, approvals, and cross-agent communication. Threat-model agent-to-agent prompt injection, malicious artifacts, privilege escalation via delegation, approval forgery, and cost-denial-of-service. Specify audit invariants.

## 20. Handoff — Integration Agent

Map A2A task/message/artifact operations into platform Task/Artifact/Event model. Define event/webhook contracts, adapter interaction during retries/cancel, and external notification hooks. Specify how runtime-native subagent/group features are either disabled, surfaced, or reconciled with platform orchestration.

## 21. Handoff — Data Design Agent

Define relational/event schemas, state transitions, idempotency keys, causation/correlation, artifact versioning, finding/decision/approval models, group policy storage, workflow template/run separation, retention, and query patterns required for activity timeline and recovery.

---

<!-- SOURCE: 05-prd-mvp4-review-quality-publish.md -->

# PRD — MVP 4: Review, Quality Gates & Controlled Publish

## 1. Purpose

Complete the local-first delivery lifecycle. Add rich code diff review, hunk/file actions, specialist review stages, automated quality gates, local commit control, explicit publish approval, remote push, PR creation, CI correlation, and clear separation between local engineering state and remote repository state.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Provide first-class workspace change review UI/API.
- Support file/hunk stage, unstage, revert, and comment workflows.
- Run QA, code-review, and security agents against local workspace/diff before publication.
- Define configurable quality gates based on tests, reviews, findings, and approvals.
- Support local commits with traceable agent/user attribution metadata.
- Publish branch using control-plane Git credentials, not agent sandbox credential.
- Create Forgejo/GitHub PR after approval.
- Track remote CI status and correlate to local task/workspace.
- Make local vs committed vs published vs PR states explicit.

## 4. Non-Goals

- Automatic merge to protected branches.
- Production deployment.
- Full enterprise policy engine (MVP8).
- Advanced context-intelligence review targeting (MVP5/6).
- Hosted code review replacement for all remote Git features.

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Local review
Agent finishes implementation. User opens changed-file panel, inspects hunks, reverts one hunk, requests agent revision, and re-runs tests.

### W2 — Specialist review
QA, Code Review, and Security agents inspect local diff/source. Findings block or pass according to policy. Implementer resolves findings before commit.

### W3 — Commit and publish
User approves local commit. Platform creates commit through Git service. User separately approves Publish. Platform pushes branch with service credential and creates PR.

### W4 — CI feedback
Remote CI result is linked back to task/workspace. Failed CI may reopen workflow before merge.

## 7. Functional Requirements

- **FR-M4-001 Diff viewer:** changed files, additions/deletions, unified/side-by-side hunks, binary-file handling.
- **FR-M4-002 File/hunk stage:** stage/unstage at file/hunk level where Git supports reliable patch application.
- **FR-M4-003 Revert:** revert selected file/hunk with confirmation and state refresh.
- **FR-M4-004 Review comments:** attach comment/finding to file/path/hunk/line with source version.
- **FR-M4-005 Review task types:** QA, Code Review, Security Review mapped to specialist agents/groups.
- **FR-M4-006 Review artifact:** verdict, findings, severity, affected source references, requested change.
- **FR-M4-007 Quality gate:** evaluate tests, review verdicts, unresolved findings, required approvals.
- **FR-M4-008 Local commit:** commit selected staged changes with controlled author/committer metadata policy.
- **FR-M4-009 Commit approval:** optional/required approval independent from publish.
- **FR-M4-010 Publish action:** push selected local branch through control-plane Git integration with implementer agent identity attribution.
- **FR-M4-011 Remote branch collision handling:** detect divergence/name collision/non-fast-forward and require resolution.
- **FR-M4-012 PR creation:** create Forgejo/GitHub pull request authored by implementer agent's remote persona with generated/user-edited title/body, issue linkage, and automated reviewer assignment.
- **FR-M4-013 Remote state:** track unpublished, published, PR open, updated after publish, remote behind/ahead.
- **FR-M4-014 CI status ingestion:** correlate checks/statuses to commit/PR.
- **FR-M4-015 Post-publish update:** allow additional local commits and republish with explicit action.
- **FR-M4-016 Review reset/invalidation:** source changes invalidate or mark stale prior tests/reviews according to scope.
- **FR-M4-017 Protected action audit:** commit/publish/PR actions record actor, policy, source SHA, resulting SHA/remote IDs.
- **FR-M4-018 Human override:** accept risk/waive finding only with permission and reason.
- **FR-M4-019 Diff size safeguards:** large/binary/generated-file handling and review warnings.
- **FR-M4-020 PR artifact:** persist remote URL/ID/status and relation to local task/workspace.
- **FR-M4-021 Remote review projection:** project internal ReviewFinding and review runs to native Forgejo/GitHub PR reviews with file/line inline comments and formal verdicts (`APPROVE`, `REQUEST_CHANGES`) as an asynchronous display projection, while internal review rework loops consume structured A2A ReviewFinding artifacts to preserve context efficiency.
- **FR-M4-022 Remote issue synchronization:** synchronize task status and assignee to remote Forgejo/GitHub issue.

## 8. Non-Functional Requirements

- Diff operations must be consistent with exact workspace Git state and detect staleness.
- Publish must be idempotent and handle network retries safely.
- Review comments/findings must preserve source anchor or clearly indicate when anchor is stale.
- CI webhook handling must be authenticated and replay-safe.
- Protected actions should complete transactionally where possible or leave explicit recoverable partial state.

## 9. Domain Entities and Data Considerations

Entities: `ReviewRun`, `ReviewFinding`, `ReviewAnchor`, `QualityGate`, `QualityGateEvaluation`, `CommitIntent`, `CommitRecord`, `PublishRequest`, `PublishResult`, `RemoteBranchState`, `PullRequest`, `CIStatus`, `RiskAcceptance`, `RemoteReviewVerdict`.

Store both local and remote commit SHA. Findings reference workspace revision/diff hash. Quality-gate evaluations are versioned snapshots, not a mutable single boolean.

## 10. Integration Requirements

- Forgejo push/PR/status APIs.
- GitHub push/PR/check status APIs.
- Git service remote credential broker.
- CI webhook/status APIs.
- Runtime agents for QA/Code Review/Security via MVP2/3.
- Git patch/staging semantics via MVP1.

## 11. Security and Trust Requirements

- Remote write credentials accessible only to trusted Git integration component.
- Publish requires explicit authorization and configurable approval.
- Branch protections on remote must be respected; platform must not bypass protections silently.
- Webhooks require signature verification/replay protection.
- Risk acceptance/waiver requires privileged role and immutable audit.
- Generated PR description must not leak secrets/runtime transcripts.
- Review agents remain untrusted and cannot self-grant publish authority.

## 12. Architecture Considerations and Constraints

- Separate `WorkspaceChangeService`, `ReviewService`, `QualityGateService`, and `RemoteGitPublicationService` logically even if initially deployed monolithically.
- Treat commit and publish as separate state transitions.
- Git service owns remote mutation and is the only component with write credential by default.
- Review/test validity should depend on workspace revision hash.
- Remote provider abstraction must preserve provider-specific capabilities rather than forcing identical PR semantics.

## 13. Observability and Telemetry

Capture diff size, review duration, findings by severity/type, rework cycles, tests/gates, commit latency, publish attempts/failures, PR creation latency, CI results, waived findings, human approval wait time, remote divergence events.

## 14. Acceptance Criteria

- Review local diff produced by an agent and revert a selected hunk before commit.
- Run QA/Code/Security reviews and block commit/publish on configured unresolved finding.
- Modify source after review and show prior review as stale.
- Create local commit without publishing.
- Demonstrate agent sandbox cannot push while control-plane Publish succeeds after approval.
- Create Forgejo PR and GitHub PR through provider abstraction.
- Receive authenticated CI result and display against correct commit/task.
- Reject publish and retain local workspace unchanged.
- Handle non-fast-forward remote branch without destructive force push by default.

## 15. Dependencies

MVP1 Git workspace; MVP2 runtime agents; MVP3 orchestration/approval/artifacts; Forgejo/GitHub write credentials and webhook configuration.

## 16. Risks and Mitigations

- **Patch/hunk edge cases:** rely on Git-native patch semantics and clear failure state.
- **Stale reviews:** revision hashes and invalidation rules.
- **Credential compromise:** narrow-scoped bot/app credentials and dedicated service.
- **Remote divergence:** never auto-force; fetch/rebase/resolve workflow.
- **AI review false confidence:** multiple gates, human inspection, severity/waiver tracking.

## 17. Open Questions

1. Should local commit author be agent identity, user, service account, or configurable co-author model?
2. Which gates block commit vs publish vs PR creation?
3. Should PR body include agent/model provenance by default?
4. How are generated/vendor files excluded or treated in review?
5. What is the default behavior when CI fails after publish?

## 18. Handoff — Architect Agent

Design local-to-remote state machine, diff/revision hashing, review invalidation, Git commit/publish service boundaries, provider abstraction, webhook/CI event flow, concurrency for multiple publishes, and recovery from partial remote mutation. Provide explicit invariants for local and remote SHAs.

## 19. Handoff — Security Agent

Define protected-action authorization, credential broker, webhook validation, remote branch protection handling, risk waiver controls, review-agent permissions, PR content leakage controls, audit evidence, and attack scenarios involving malicious branches/hooks/PR metadata.

## 20. Handoff — Integration Agent

Specify Forgejo and GitHub push/PR/status/check integrations, auth mechanism options, error mapping, webhook subscriptions, rate-limit behavior, remote branch reconciliation, and provider-specific capability matrix. Define CI adapter contract for future systems.

## 21. Handoff — Data Design Agent

Define review/finding/anchor schemas, workspace revision hash, quality gate snapshots, commit/publish/PR entities, local-vs-remote lineage, CI status history, waiver records, and stale-data invalidation. Include indexing/query needs for task review UI.

---

<!-- SOURCE: 06-prd-mvp5-repository-intelligence.md -->

# PRD — MVP 5: Repository Intelligence

## 1. Purpose

Build a repository intelligence substrate that reduces blind exploration. Index source structure deterministically where possible, maintain symbol and relationship graphs, add lexical and semantic retrieval, enrich with Git/test/spec metadata, support workspace overlays, and return provenance-linked candidate scope for source verification.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Parse supported languages into files/symbols/relationships using deterministic tooling where feasible.
- Build queryable code relationship graph for imports, calls/references where available, inheritance/implementation, tests, dependencies.
- Add lexical/full-text retrieval optimized for identifiers, error strings, API names, config keys.
- Add vector/semantic retrieval for conceptual search.
- Fuse retrieval modes and expose a stable Repository Intelligence API.
- Track Git commit/version provenance and active workspace overlay.
- Support impact/blast-radius queries and candidate test discovery.
- Always provide source references so runtimes can read canonical code before edits.

## 4. Non-Goals

- Fully sound whole-program static analysis for every language.
- Guarantee that graph relationships are complete/correct enough to replace source reading.
- Autonomous code modification by intelligence service.
- Final role-aware context budgeting (MVP6).
- Cross-organization global knowledge graph.

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Index base repository
After fetch, platform indexes supported files, symbols, relationships, lexical terms, embeddings, and Git metadata for pinned commit.

### W2 — Issue exploration
Query `hub key rotation` returns lexical, semantic, and graph candidates with source paths/symbols and relevance evidence.

### W3 — Impact analysis
Given changed symbol, system returns likely callers, dependents, tests, API surfaces, and related specs with confidence/provenance.

### W4 — Workspace overlay
Agent modifies code in worktree. Intelligence updates/overlays changed symbols so reviewers query current workspace state instead of stale main.

## 7. Functional Requirements

- **FR-M5-001 Repository index job:** build/version intelligence snapshot for repository commit.
- **FR-M5-002 Language detection/parser registry:** identify supported languages and parser capability.
- **FR-M5-003 Symbol extraction:** files/modules/classes/functions/methods/interfaces/types/constants where parser supports.
- **FR-M5-004 Relationship extraction:** contains/imports/calls/references/extends/implements/tests/depends-on with provenance/confidence.
- **FR-M5-005 Lexical index:** identifier/path/content/error/config search with ranking.
- **FR-M5-006 Vector index:** embedding generation/storage/search with configurable model/backend.
- **FR-M5-007 Hybrid search API:** execute lexical + semantic + graph retrieval and return scored candidates.
- **FR-M5-008 Graph query API:** neighbors, shortest relevant path, callers/callees, import/dependency traversal, impacted tests.
- **FR-M5-009 Source provenance:** candidate links to repository, commit/workspace revision, path, line/symbol range where possible.
- **FR-M5-010 Git enrichment:** recent commits touching candidate, changed-together signals, blame/history metadata where configured.
- **FR-M5-011 Test mapping:** associate tests with modules/symbols through static relation and history heuristics.
- **FR-M5-012 Spec/doc linkage:** index selected Markdown/docs/ADRs/issues and link references to code where derivable.
- **FR-M5-013 Incremental indexing:** update changed files without mandatory full rebuild where backend supports reliable updates.
- **FR-M5-014 Workspace overlay:** represent task changes separately from immutable/base index.
- **FR-M5-015 Consistency check:** detect stale index vs repository/workspace revision.
- **FR-M5-016 Rebuild:** full rebuild path when incremental state is suspect.
- **FR-M5-017 Provider abstraction:** Graphify/other graph extractor and Neo4j/other backends are replaceable implementations.
- **FR-M5-018 Retrieval explanation:** return why candidate matched (lexical, semantic, graph relation, history, explicit reference).
- **FR-M5-019 Source fetch:** canonical file/symbol content can be retrieved by candidate reference.
- **FR-M5-020 Index health:** per repo/workspace status, parser failures, unsupported files, freshness.

## 8. Non-Functional Requirements

- Indexing must be asynchronous and not block normal Git operations.
- Base index is versioned by commit or explicit generation.
- Unsupported language/file must fail gracefully and remain searchable lexically where possible.
- Search latency target for warm repository: p95 <= 2s for normal interactive hybrid query excluding expensive external embedding generation.
- Incremental update must not silently claim freshness when failed.
- Embedding provider must be configurable/local-capable for privacy/cost.

## 9. Domain Entities and Data Considerations

Entities: `RepositoryIndex`, `IndexGeneration`, `SourceFile`, `Symbol`, `Relationship`, `RelationshipProvenance`, `LexicalDocument`, `EmbeddingRecord/Reference`, `GitHistoryFact`, `TestAssociation`, `DocReference`, `WorkspaceIndexOverlay`, `RetrievalQuery`, `RetrievalCandidate`.

Graph nodes/edges require stable logical identity strategy across commits while preserving version lineage. Derived relationships need confidence and extraction method. Do not store source content redundantly without retention/consistency plan.

## 10. Integration Requirements

- Parser/AST framework such as tree-sitter or equivalent.
- Optional Graphify integration as a repository graph extractor/exporter.
- Graph backend abstraction, with Neo4j a candidate due to graph/vector/full-text capabilities.
- Embedding provider abstraction supporting local OpenAI-compatible and cloud providers.
- Git history and workspace service.
- Issue/spec ingestion sources.

No single graph/vector technology is mandatory at product-contract level.

## 11. Security and Trust Requirements

- Repository source and embeddings may contain sensitive IP; support local-only indexing mode.
- Index backends must enforce project/repository isolation.
- Queries must not cross repositories/projects without explicit permission.
- Derived docs/embeddings follow source retention/access policy.
- Do not execute repository code during indexing unless explicitly sandboxed.
- Treat parser/indexer inputs as untrusted; resource-limit parsing.
- Source fetch honors workspace permissions.

## 12. Architecture Considerations and Constraints

- Separate extraction, storage, retrieval, and source-fetch interfaces.
- Canonical source remains Git/workspace; index is derived/cache-like and rebuildable.
- Workspace overlay design is critical; avoid mutating shared base graph for every task.
- Support capability-specific relationship accuracy rather than pretending complete call graph.
- Consider Reciprocal Rank Fusion or pluggable fusion, but keep algorithm configurable.
- Design provenance as first-class to support later context verification.

## 13. Observability and Telemetry

Capture index duration, files/symbols/edges, unsupported parser rate, extraction errors, incremental update time, index freshness lag, lexical/vector/graph query latency, result counts, source fetches, rebuild frequency, storage size, embedding token/cost.

## 14. Acceptance Criteria

- Index a representative mixed-language repository and enumerate symbols/relationships with provenance.
- Exact identifier query returns correct symbol through lexical search.
- Conceptual query returns relevant files/symbols through vector search.
- Graph query finds direct dependents and likely tests for a changed symbol.
- Hybrid query returns ranked candidates with match explanation.
- Modify workspace file and show overlay query differs from base repository query.
- Simulate failed incremental index and show stale/failed health rather than incorrect `fresh` state.
- Rebuild index from source and reproduce usable retrieval state.
- Runtime can use candidate reference to read actual source before modification.

## 15. Dependencies

MVP1 repository/workspace source access; artifact storage; background job processing; optional embedding/model access; graph/vector/lexical backend selection.

## 16. Risks and Mitigations

- **Graph inaccuracies:** confidence/provenance, source verification, rebuild path.
- **Incremental index corruption:** generation IDs, overlay isolation, health checks.
- **Embedding cost/privacy:** configurable local models and selective indexing.
- **Language coverage gaps:** parser registry and lexical fallback.
- **Storage growth:** index retention/compaction and version policy.

## 17. Open Questions

1. Which languages are Tier-1 for deterministic graph support?
2. Should base graph be per default branch head, per commit, or rolling generation with source SHA references?
3. How are deleted/renamed symbols tracked across commits?
4. Which fusion algorithm is default and how is it evaluated?
5. How much Git history is indexed by default?
6. Should docs/specs share same graph or separate linked indexes?

## 18. Handoff — Architect Agent

Design intelligence service boundaries, parser/extractor pipeline, graph/lexical/vector backend contracts, index generation/versioning, workspace overlay architecture, rebuild/incremental strategy, retrieval API, provenance model, and scale characteristics. Evaluate Graphify+Neo4j as one implementation but keep interfaces replaceable.

## 19. Handoff — Security Agent

Define repository/index isolation, IP/privacy handling, local-only mode, parser sandbox/resource limits, backend access control, embedding-provider data exposure policy, source-fetch authorization, and retention/deletion requirements.

## 20. Handoff — Integration Agent

Specify contracts for parser registry, Graphify optional adapter, graph store, lexical store, vector/embedding providers, Git history ingestion, issue/spec sources, and source retrieval. Document failure/fallback behavior when one retrieval backend is unavailable.

## 21. Handoff — Data Design Agent

Define versioned schemas/IDs for files/symbols/relationships, provenance/confidence, index generations, embeddings, lexical docs, history facts, workspace overlays, retrieval candidates, and stale/fresh states. Propose logical identity across commits and deletion/rename lineage.

---

<!-- SOURCE: 07-prd-mvp6-context-intelligence.md -->

# PRD — MVP 6: Context Intelligence & Token Economics

## 1. Purpose

Turn repository intelligence into role-aware, measurable context optimization. Build a Context Engine that classifies task information needs, combines graph/lexical/vector/history/artifact evidence, retrieves canonical source, deduplicates and budgets content, generates versioned context packs, and adaptively escalates when evidence is insufficient. Make token/cost efficiency visible alongside engineering quality.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Generate role-specific context packs for implementation, QA, code review, security, architecture, integration, and data design.
- Fuse repository intelligence with issue/task/workspace/artifact state.
- Enforce configurable token budgets while preserving source provenance.
- Deduplicate overlapping source/evidence.
- Implement adaptive context escalation instead of fixed maximum context.
- Reuse durable artifacts rather than replay full conversations.
- Measure tokens/cost/context avoided per task/agent.
- Benchmark savings together with correctness/test/review outcomes.
- Support optional last-mile compression but never make it the sole retrieval mechanism.

## 4. Non-Goals

- Training a proprietary reranker/model.
- Guaranteeing identical output to full-repository context.
- Replacing runtime-native prompt caching.
- Hard dependency on 9Router/Headroom/RTK.
- Automatic policy learning from production without human control.

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Implementer context
Issue enters implementation. Context Engine retrieves requirements, relevant symbols/files/tests/API contracts, loads canonical source, budgets to target tokens, and sends Context Pack to runtime.

### W2 — Security context
Same task enters Security Review. Engine prioritizes diff, auth/secrets/trust-boundary source, related callers/dependencies, security artifacts, and omits unrelated implementation details.

### W3 — Escalation
Agent reports ambiguity/missing evidence. Engine expands from snippets to whole files/modules or wider graph neighborhood within policy and records escalation reason.

### W4 — Economics
Task dashboard compares repository size, retrieved candidates, sent tokens, cached/compressed tokens where available, model output, cost, and quality outcome.

## 7. Functional Requirements

- **FR-M6-001 Context request:** task, agent/role, objective, workspace revision, budget, retrieval policy.
- **FR-M6-002 Query planner:** derive one or more retrieval queries/intents from task and role.
- **FR-M6-003 Multi-source retrieval:** repository graph, lexical, vector, Git history, issue, specs, prior artifacts, current diff/tests/findings.
- **FR-M6-004 Fusion/rerank:** combine candidate sources with configurable scoring/reranker.
- **FR-M6-005 Graph expansion:** selectively add neighbors/dependencies/tests based on role/query.
- **FR-M6-006 Canonical source loading:** replace/augment derived summaries with actual source excerpts/files before final pack where required.
- **FR-M6-007 Deduplication:** eliminate duplicate/overlapping chunks and repeated artifacts.
- **FR-M6-008 Token estimation:** estimate per content item and total before sending.
- **FR-M6-009 Budget allocator:** prioritize mandatory/optional context according to role/policy.
- **FR-M6-010 Context Pack:** immutable/versioned package with instructions, evidence, source refs, omissions, budget, generation metadata.
- **FR-M6-011 Context tiers:** at minimum summary/graph, snippets, full relevant files/sections, expanded module/repo scope.
- **FR-M6-012 Escalation request:** runtime can request more context with reason/category.
- **FR-M6-013 Conflict detection:** detect contradictory/stale evidence where possible and escalate source breadth.
- **FR-M6-014 Artifact reuse:** consume typed prior artifacts without full raw transcript.
- **FR-M6-015 Role policies:** configurable context profile per role/group/stage.
- **FR-M6-016 Token telemetry:** requested/retrieved/selected/sent/output tokens, cache/compression when provider reports.
- **FR-M6-017 Avoided context metric:** compare estimated available repo context to actual sent context with clear methodology.
- **FR-M6-018 Cost telemetry:** provider/model rate input when available/configured, cost per execution/task.
- **FR-M6-019 Quality correlation:** associate context pack with test/review/final task outcome.
- **FR-M6-020 Compression provider interface:** optional integration with RTK/Headroom/other compressor after selection.
- **FR-M6-021 Context audit:** show exactly which source/artifact was included and omitted.
- **FR-M6-022 Reproducibility metadata:** repository/workspace revision and index generation used for context pack.

## 8. Non-Functional Requirements

- Context building target p95 <= 5s for warm indexes excluding external model-based reranking where configured.
- Token estimates may be approximate but methodology/version must be recorded.
- Context selection must be deterministic enough to diagnose/replay under same policy/index generation, acknowledging model-based rerank variance.
- No context compression step may remove source provenance.
- Context failures fall back to broader source retrieval rather than silent empty context.
- Large files require safe truncation/chunk policy with explicit omission markers.

## 9. Domain Entities and Data Considerations

Entities: `ContextRequest`, `ContextPolicy`, `RoleContextProfile`, `RetrievalPlan`, `RetrievalRun`, `ContextCandidate`, `ContextSelection`, `ContextPack`, `ContextPackItem`, `ContextEscalation`, `TokenUsage`, `CostRecord`, `CompressionRecord`, `QualityOutcome`, `ContextBenchmarkRun`.

ContextPack items must reference source version/provenance and indicate content type (`source`, `derived`, `artifact`, `instruction`). Store policy/model/index versions used to generate selection.

## 10. Integration Requirements

- MVP5 Repository Intelligence.
- MVP3 typed artifacts/task roles.
- Runtime/model usage telemetry from MVP2.
- Optional reranker/embedding/inference provider.
- Optional 9Router compression/routing integration later via common inference interface.

Context engine must work even when optional compressor/gateway is absent.

## 11. Security and Trust Requirements

- Context retrieval must respect repository/project/role permissions.
- Do not expose secrets from unrelated files simply because semantically relevant.
- Treat retrieved repository text as untrusted content; separate system instructions from source evidence.
- Preserve provenance labels to mitigate prompt injection from code/docs/issues.
- Context packs may contain sensitive IP and must follow retention/access controls.
- Cost/token telemetry must not leak prompt/source content to unauthorized observers.
- Escalation cannot broaden access beyond agent permission scope.

## 12. Architecture Considerations and Constraints

- Context Engine should be a separate service/module boundary from Repository Intelligence and Inference Gateway.
- Retrieval providers return candidates; Context Engine owns selection/budget/source verification.
- Keep role policy declarative and versioned.
- Separate token optimization metrics from quality metrics to prevent optimizing the wrong target.
- Support benchmark harness comparing baseline runtime-only execution against context-assisted execution.
- Optional compressor must be a final-stage provider, not architectural dependency.

## 13. Observability and Telemetry

Capture candidate counts by source, retrieval latency, rerank latency, context-build latency, tokens by stage, source/derived ratio, escalation count/reason, cache/compression metrics, cost, selected files/symbols, final files changed, tests/review results, task success. Provide per-agent/task/project dashboards.

## 14. Acceptance Criteria

- Generate distinct context packs for Implementer and Security on same task and show materially different content selection.
- Every source excerpt in pack links to canonical repository/workspace revision.
- Enforce 10k token budget and show prioritized omissions when candidates exceed budget.
- Agent requests more context; system escalates tier and records why/what changed.
- If vector backend is unavailable, build usable pack from lexical/graph/source fallback.
- Run benchmark set comparing baseline harness-only token usage to Context Engine usage with same model and issue set.
- Demonstrate token reduction while maintaining agreed quality threshold (tests/review success) on benchmark set.
- Show context/cost dashboard with transparent metric definitions.

## 15. Dependencies

MVP5 intelligence, MVP3 roles/artifacts, model/token telemetry, benchmark repository/issues, tokenizer/cost configuration.

## 16. Risks and Mitigations

- **Over-compression harms quality:** adaptive escalation, quality correlation, canonical source.
- **Misleading savings metric:** published methodology and benchmark baselines.
- **Retriever misses key file:** multiple retrieval modes and runtime escalation.
- **Prompt injection in retrieved text:** provenance labels, instruction/data separation, least privilege.
- **Reranker cost negates savings:** local/cheap reranker option and telemetry.

## 17. Open Questions

1. Which role context profiles ship as defaults?
2. What quality threshold is acceptable for claiming token savings?
3. Should context packs persist full included content or references plus generated snapshots?
4. Which tokenizer is used for model-agnostic preflight estimates?
5. How should agent request additional context in A2A/runtime-neutral form?
6. When should whole-file retrieval be mandatory rather than excerpts?

## 18. Handoff — Architect Agent

Design Context Engine service boundaries, retrieval planning/fusion/rerank pipeline, policy model, context-pack schema, token-budget algorithm, escalation protocol, source verification, benchmark architecture, and failure/fallback modes. Keep compression/inference gateway pluggable.

## 19. Handoff — Security Agent

Define permissions filtering before/after retrieval, prompt-injection boundaries, source-vs-instruction labeling, sensitive-file/secret exclusion, context pack access/retention, escalation authorization, telemetry privacy, and threat scenarios where malicious repository content attempts to influence agent/system policy.

## 20. Handoff — Integration Agent

Specify integration contracts to Repository Intelligence, runtime adapters, tokenizers, model usage APIs, rerankers, optional compressors, and inference gateways. Define normalized token/cache/compression telemetry and fallback behavior when provider usage data is incomplete.

## 21. Handoff — Data Design Agent

Define schemas and lineage for ContextRequest/Plan/Candidate/Selection/Pack/Escalation/Usage/Cost/Quality. Specify immutable context-pack versioning, source references, content hashing, policy/index/model version capture, retention, and benchmark-result schema.

---

<!-- SOURCE: 08-prd-mvp7-integrations-inference.md -->

# PRD — MVP 7: Integrations & Inference Fabric

## 1. Purpose

Expand the platform into an integration and inference fabric without sacrificing vendor neutrality. Standardize Git providers, MCP/tool integrations, CI/CD, model/provider routing, local-model endpoints, and optional inference gateways such as 9Router or LiteLLM behind stable product contracts.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Formalize provider interfaces for Forgejo/GitHub and future Git hosts.
- Add MCP registry/configuration and role-scoped tool access.
- Integrate CI/CD status/actions through provider abstraction.
- Add inference provider/gateway abstraction for direct cloud, local OpenAI-compatible, 9Router, LiteLLM, CLIProxyAPI-style gateways.
- Support model routing policies by task/role/cost/capability.
- Track quota, fallback, cache, compression, usage where provider exposes them.
- Support local models for low-cost extraction/classification while preserving frontier models for high-value reasoning.
- Centralize integration health, credentials, and capability discovery.

## 4. Non-Goals

- Building a new model gateway from scratch.
- Replacing MCP/A2A with proprietary protocols.
- Supporting every Git/model/CI provider in first release.
- Autonomous production deployment.
- Enterprise-wide policy administration (MVP8).

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Model routing
Architecture review uses frontier model; indexing helper uses local model; fallback routes to secondary provider when quota/rate limit policy allows.

### W2 — MCP tools
Security agent receives read-only security documentation and scanner MCP tools; implementation agent receives repo/build tools but not security secrets.

### W3 — CI integration
After PR creation, provider/webhook updates CI status and workflow reacts to pass/fail.

### W4 — Gateway swap
User changes inference backend from direct provider to 9Router/LiteLLM without changing Agent/Task/workflow definitions.

## 7. Functional Requirements

- **FR-M7-001 GitProvider interface:** repo metadata, issue/PR, branch, status/checks, webhooks, comments, multi-user agent identity routing, and PR review submissions as supported.
- **FR-M7-002 Forgejo provider:** complete targeted provider implementation.
- **FR-M7-003 GitHub provider:** complete targeted provider implementation.
- **FR-M7-004 MCP Server registry:** register endpoint/transport, capabilities, credentials, health, allowed roles/projects.
- **FR-M7-005 Tool policy:** allow/deny MCP tools per agent/task/group.
- **FR-M7-006 CIProvider interface:** status/check ingestion, optional rerun/cancel actions where supported.
- **FR-M7-007 InferenceProvider interface:** list models/capabilities, invoke supported API shape, usage metadata, health.
- **FR-M7-008 Direct OpenAI/Anthropic-style providers:** at least one direct frontier provider path.
- **FR-M7-009 OpenAI-compatible local endpoint:** local llama.cpp/vLLM/etc through standardized interface.
- **FR-M7-010 Gateway adapters:** 9Router and LiteLLM; additional gateway adapter pattern documented.
- **FR-M7-011 Model policy:** role/task default, required capabilities, max cost/context, preferred/fallback models.
- **FR-M7-012 Fallback:** explicit retry/fallback policy distinguishes transient error, quota/rate limit, model incompatibility, content/policy error.
- **FR-M7-013 Usage normalization:** input/output/cache/compressed tokens and provider request IDs where available.
- **FR-M7-014 Quota/health:** provider health and quota hints displayed without assuming universal availability.
- **FR-M7-015 Prompt caching metadata:** capture cache hits/writes if provider exposes.
- **FR-M7-016 Compression integration:** optional 9Router RTK/Headroom-like capabilities represented as provider features, not product assumptions.
- **FR-M7-017 Credential references:** integrations store secret references, not plaintext in task definitions.
- **FR-M7-018 Capability negotiation:** model/tool/provider requirements validated before task starts.
- **FR-M7-019 Integration health dashboard:** status/version/last error/credential expiry where available.
- **FR-M7-020 Webhook event normalization:** external provider events map to typed internal events.
- **FR-M7-021 Brokered agent identity provider:** execute remote repository operations on behalf of specific agent identities while keeping credential custody centralized in control plane.

## 8. Non-Functional Requirements

- Provider outages must degrade gracefully and expose actionable state.
- Retries/fallback must avoid duplicate irreversible tool actions.
- Integration secrets must be rotatable without recreating workflows.
- Rate limits and backoff must be provider aware.
- Model response streaming should be supported where runtime path benefits.
- Normalized telemetry must preserve raw provider metrics for diagnostics.

## 9. Domain Entities and Data Considerations

Entities: `Integration`, `IntegrationCredentialRef`, `ProviderCapability`, `MCPServer`, `MCPTool`, `ToolPolicy`, `InferenceProvider`, `ModelDescriptor`, `ModelPolicy`, `InferenceRoute`, `InferenceAttempt`, `UsageRecord`, `QuotaSnapshot`, `CIProvider`, `ExternalWebhookEvent`.

Model identity must include provider + canonical provider model ID + optional alias. Routing aliases are policy objects, not canonical model identity.

## 10. Integration Requirements

- Forgejo API/webhooks.
- GitHub API/webhooks.
- MCP clients/transports.
- CI status/check interfaces.
- OpenAI-compatible APIs.
- Anthropic/direct provider APIs as chosen.
- 9Router/LiteLLM gateway APIs/config.
- Local inference endpoints.

Every adapter needs health/version/capability and normalized error mapping.

## 11. Security and Trust Requirements

- Central secret references and least-privilege credentials.
- Tool access controlled by agent/task/project; never inherit all MCP tools by default.
- Validate and authenticate webhooks.
- Prevent SSRF through arbitrary integration endpoints using allowlist/network policy where appropriate.
- Inference gateways/providers receive only task context they are authorized to process.
- Support data-residency/local-only inference policy.
- Model fallback must not silently send sensitive data to a less-trusted provider.
- Log provider IDs/usage without logging sensitive prompt bodies by default.

## 12. Architecture Considerations and Constraints

- Use adapter/plugin boundaries for Git, MCP, CI, Inference.
- Keep routing policy separate from runtime adapter; runtime asks for logical model capability, inference layer resolves route where integration model allows.
- Distinguish model invocation done by harness directly from invocation proxied through platform; support both and normalize telemetry where possible.
- Provider capabilities are discoverable/versioned.
- Avoid making 9Router mandatory; it is a high-value optional gateway implementation.

## 13. Observability and Telemetry

Capture provider health, request latency, retries/fallback, model, input/output/cache/compressed tokens, quota/rate-limit events, MCP tool call duration/errors, webhook latency/replay rejects, CI updates, credential expiry warnings, per-provider cost.

## 14. Acceptance Criteria

- Switch a configured agent workflow between direct provider and 9Router without changing task/workflow definitions.
- Use local OpenAI-compatible model for an extraction task and frontier model for architecture task under policy.
- Trigger controlled fallback on rate limit and show all attempts/usage.
- Register MCP server and enforce different tool visibility for two agent roles.
- Receive signed Forgejo/GitHub/CI webhook and normalize event.
- Demonstrate provider trust policy prevents sensitive context fallback to disallowed provider.
- Rotate integration credential without recreating project/workflow.

## 15. Dependencies

MVP2 runtime fabric, MVP4 Git/CI lifecycle, MVP6 token telemetry/context packs, secrets foundation, external provider accounts.

## 16. Risks and Mitigations

- **Provider churn:** adapter conformance/version testing.
- **Telemetry inconsistency:** normalized schema plus raw provider metadata.
- **Unsafe fallback:** trust-classification and explicit routing policy.
- **Tool over-permission:** deny-by-default role/task tool policy.
- **Gateway lock-in:** direct-provider path and provider interface.

## 17. Open Questions

1. Which model/provider capabilities are mandatory metadata?
2. Should routing occur platform-side or mostly inside gateway adapters?
3. How are harness-managed subscriptions (e.g. CLI OAuth) represented safely?
4. Which MCP transports are Tier-1?
5. How should provider trust/data residency categories be modeled?

## 18. Handoff — Architect Agent

Define plugin architecture for Git/MCP/CI/Inference providers, capability negotiation, routing/fallback policy, harness-direct vs platform-proxied inference, health management, webhook/event normalization, and extension SDK. Evaluate how 9Router fits without leaking its concepts into core domain.

## 19. Handoff — Security Agent

Define integration secret lifecycle, provider trust tiers/data residency, SSRF/network controls, MCP tool authorization, webhook authentication, safe fallback constraints, CLI subscription credential isolation, and sensitive telemetry logging rules.

## 20. Handoff — Integration Agent

Produce detailed adapter contracts for Forgejo, GitHub, MCP, CI, direct model providers, local OpenAI-compatible endpoints, 9Router, LiteLLM. Include auth, rate limits, capabilities, errors, health, webhooks, usage fields, and conformance tests.

## 21. Handoff — Data Design Agent

Define Integration/Provider/Model/Route/Attempt/Usage/Tool/Policy schemas, model alias vs canonical identity, capability versioning, quota snapshots, credential references, webhook event deduplication, and cost aggregation dimensions.

---

<!-- SOURCE: 09-prd-mvp8-governance-scale.md -->

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

---

<!-- SOURCE: 10-traceability-matrix.md -->

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

---

<!-- SOURCE: remote-agent-identities-and-sdlc.md -->

# Remote Agent Identities, Authentication, and Human-Like SDLC Collaboration

**Status:** Proposed
**Owner:** Product / Integration
**Applies to:** Forgejo and GitHub integrations across MVP2, MVP3, MVP4, and MVP7
**Traceability:** `FR-M2-001`, `FR-M2-005`, `FR-M3-008`, `FR-M3-009`, `FR-M3-011`, `FR-M3-012`, `FR-M3-014`, `FR-M4-004`, `FR-M4-006`, `FR-M4-007`, `FR-M4-010`, `FR-M4-012`, `FR-M7-001`, `FR-M7-002`, `FR-M7-003`, `FR-M8-007`, `FR-M8-021`, `ADR-0003`

---

## 1. Executive Summary & Vision

Agnest is designed to operate heterogeneous AI coding agents as a coordinated engineering organization. While Agnest is local-first, software development remains inherently collaborative. In real-world engineering teams, collaboration happens on remote Git hosts (Forgejo and GitHub).

This specification introduces the **Brokered Remote Agent Identity** model. Instead of hiding multi-agent workflows behind an anonymous single system bot, each specialist agent operates as a first-class engineering team member with a recognized identity in the remote repository:
- Issues are assigned to specific agents (e.g. `@agnest-implementer`).
- Branches and Pull Requests are published with explicit author attribution to the implementer agent.
- Specialist agents (`@agnest-qa`, `@agnest-codereview`, `@agnest-security`) conduct native PR reviews, post file/hunk inline comments, and submit formal verdicts (`APPROVE` or `REQUEST_CHANGES`).
- The entire Software Development Life Cycle (SDLC) is transparently observable to human engineers on Forgejo/GitHub, just like collaboration among human engineers.
- **Critical Security Invariant:** Task sandboxes remain air-gapped from remote write credentials (**Principle P9: Local-First, Remote-by-Approval**). Remote API interactions are strictly brokered by the Agnest Control Plane.

---

## 2. The Brokered Remote Identity Pattern

### 2.1 Core Architectural Separation

```text
+-----------------------------------------------------------------------------------------+
| REMOTE COLLABORATION HOST (Forgejo / GitHub)                                            |
|                                                                                         |
|   Issue #42   --> Assignee: @agnest-implementer                                         |
|   PR #10      --> Author:   @agnest-implementer                                         |
|                   Reviewer: @agnest-qa          [APPROVE]                               |
|                   Reviewer: @agnest-codereview  [CHANGES_REQUESTED: inline comments]    |
|                   Reviewer: @agnest-security    [APPROVE]                               |
+-----------------------------------------------------------------------------------------+
                                         ▲
                         Brokered Provider API Calls
                         (Assign, Push, PR, Review, Comment)
                                         │
+----------------------------------------┴------------------------------------------------+
| AGNEST CONTROL PLANE                                                                    |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   | Remote Identity & Credential Broker                                             |   |
|   |   - Agent "Hephaestus" -> Remote: @agnest-implementer (Token Ref: SEC-FJO-IMP)  |   |
|   |   - Agent "Argus"      -> Remote: @agnest-qa          (Token Ref: SEC-FJO-QA)   |   |
|   |   - Agent "Athena"     -> Remote: @agnest-codereview  (Token Ref: SEC-FJO-CR)   |   |
|   |   - Agent "Sentry"     -> Remote: @agnest-security    (Token Ref: SEC-FJO-SEC)  |   |
|   +---------------------------------------------------------------------------------+   |
|                                         ▲                                               |
|                    Emits Typed Artifacts, Diffs, Findings                               |
|                                         │                                               |
|   +-------------------------------------┴-------------------------------------------+   |
|   | LOCAL TASK SANDBOXES (Incus)                                                    |   |
|   |   - Sandbox Hephaestus: Modifies local worktree & runs tests                    |   |
|   |   - ZERO remote Git credentials inside sandbox filesystem or environment        |   |
|   +---------------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------------+
```

### 2.2 Security Invariants
1. **Zero Remote Write Credentials in Sandboxes (`FR-M1-017`, `ADR-0003`):** No Personal Access Token (PAT), SSH private key with write access, or OAuth token ever enters the task sandbox filesystem or environment. Direct `git push` inside the sandbox fails by default.
2. **Centralized Credential Custody:** Tokens corresponding to agent remote accounts are stored in the Control Plane Secret Store (`FR-M8-007`).
3. **Brokered Execution:** When an agent produces an artifact (e.g. `ReviewFinding`, `PublishRequest`), the Control Plane verifies the quality gate / human approval, binds the action to that agent's `ExternalAgentIdentity`, and calls the remote Forgejo/GitHub API using the agent's brokered credentials.

### 2.3 Dual-Layer Architecture: Execution Bus (A2A) vs Display Projection (Remote Git)

A fundamental architectural principle governs all multi-agent interactions across both Workflow and Deliberation modes:

1. **Internal Execution Bus (100% A2A & Typed Artifacts):**
   - Agents communicate internally exclusively through **Agent2Agent (A2A)** semantics and typed structured artifacts (`ReviewFinding`, `ImplementationSummary`, `TestRun`, `Finding`).
   - **Context Efficiency Guarantee (Principle P7):** Agents **never** scrape, fetch, or parse raw HTML/markdown comment threads from Forgejo/GitHub. Scraping remote threads would cause severe token bloat, parsing errors, hallucination, and prompt injection vulnerabilities.
   - In rework loops (`FR-M3-014`), the Implementer Agent receives concise, structured `ReviewFinding` references within its role-tailored Context Pack (~50 tokens), avoiding thousands of wasted tokens on conversational overhead.
2. **External Display Projection (Asynchronous Remote Git Sync):**
   - Comments on PRs (inline hunk reviews) and Issues (round positions) are **asynchronous display projections** created by the Control Plane via provider REST APIs.
   - Generating these remote comments costs **$0 and 0 additional LLM tokens**; it is pure backend API orchestration.
   - This provides complete human-in-the-loop transparency on Forgejo/GitHub while preserving maximum context economics and speed in the agent runtime.

---

## 3. Remote Host Implementations

### 3.1 Forgejo Implementation (Dedicated Machine Users)
In Forgejo instances:
- Dedicated user accounts are provisioned for standard engineering roles:
  - `@agnest-architect`
  - `@agnest-implementer`
  - `@agnest-qa`
  - `@agnest-codereview`
  - `@agnest-security`
- Accounts belong to the repository organization with tailored role permissions:
  - Implementer: *Write* (create branches, open PRs).
  - Reviewers: *Triage / Write* (post comments, submit PR reviews).
- Authentication: Scoped Personal Access Tokens (PATs) or OAuth Application credentials bound to normalized canonical origins (`scheme, host, effective port`).

### 3.2 GitHub Implementation (GitHub Apps & Machine Users)
In GitHub repositories:
- **GitHub Apps (Recommended):** An Agnest GitHub App installation with bot slugs (e.g. `agnest-implementer[bot]`, `agnest-reviewer[bot]`). This provides fine-grained repository permissions, webhook signature validation, and compliant attribution without violating user seat policies.
- **Machine Users (Alternative):** Dedicated GitHub user accounts registered with collaborator permissions where enterprise policy permits.

---

## 4. End-to-End Human-Like SDLC Workflow

### 4.1 Workflow Mode (Feature Delivery & Bug Fixing)

```text
[Human Owner] creates Issue #42: "Fix login session timeout"
     │
     ▼
[Control Plane] imports Issue, creates Task TSK-0142
     │
     ▼ (Forgejo API call)
[Remote Issue #42] Assignee updated to @agnest-implementer; label 'status: in-progress'
     │
     ▼
[Implementer Agent] works in local Incus sandbox -> runs tests -> passes local suite
     │
     ▼ (Human / Policy Approval Gate)
[Control Plane] executes Publish via @agnest-implementer credential:
     ├─ Pushes branch 'fix/login-session-timeout'
     └─ Opens PR #10 (Author: @agnest-implementer, "Fixes #42")
     │
     ▼
[Control Plane] Requests Reviewers on PR #10:
     ├─ @agnest-qa
     ├─ @agnest-codereview
     └─ @agnest-security
     │
     ▼
[Specialist Multi-Agent Reviews]:
     ├─ @agnest-qa runs test matrix -> submits PR Review: APPROVE ("Test suite passed, 0 regressions")
     ├─ @agnest-codereview inspects diff -> submits PR Review: REQUEST_CHANGES
     │    └─ Inline comment on auth/session.go:L45: "Sanitize token before caching"
     └─ @agnest-security inspects threat model -> submits PR Review: APPROVE
     │
     ▼ (Rework Loop: FR-M3-014)
[Implementer Agent] receives review findings in local workspace -> amends code -> passes tests
     │
     ▼
[Control Plane] pushes revised commit -> requests re-review
     │
     ▼
[@agnest-codereview] verifies fix -> updates verdict to APPROVE
     │
     ▼ (Quality Gate Passed: FR-M4-007)
[Human Owner] inspects clean PR #10 with all reviews passing -> clicks MERGE
```

### 4.2 Deliberation Mode (Architecture & Design Discussions)
When multi-agent reasoning is required before implementation:
1. **Remote RFC Issue:** An issue tagged `deliberation` or `design` is created on Forgejo/GitHub (e.g. Issue #50: *"RFC: Database choice for telemetry cache"*).
2. **Round-Based Positions:** Specialist agents are mentioned (`@agnest-architect`, `@agnest-security`, `@agnest-datadesign`).
3. **Structured Contributions:** In Round 1, each agent posts an independent position comment analyzing trade-offs, constraints, and risks.
4. **Anti-Spam & Silence Guardrails (`FR-M3-012`):** Agents without novel input produce no comments ("silence is valid"). Chatty conversational pleasantries are prohibited.
5. **Coordinator Synthesis & ADR PR (`FR-M3-008`):** The nominated coordinator summarizes consensus and unresolved trade-offs, then publishes a single ADR Pull Request.

### 4.3 Bi-Directional Human Interaction: Remote Issue Comments vs Agnest Dashboard

Agnest supports flexible, bi-directionally synchronized interaction for human engineers and Product Owners:

1. **Interacting via Remote Issue Comments (Forgejo / GitHub):**
   - Human leads can participate by commenting directly in the Forgejo/GitHub Issue or PR thread.
   - External Webhook integration (`FR-M7-020`) validates the commenter identity and privileges (`author_association: OWNER | MEMBER`).
   - The comment is ingested, normalized, and injected directly into the next deliberation or review round as a high-priority `HumanInstruction` within the agent Context Pack.
   - Allows seamless participation from mobile devices or standard Git web interfaces without opening the Agnest dashboard.
2. **Interacting via Agnest Dashboard UI (Experience Layer / Deliberation View):**
   - Human leads can monitor deliberation or workflow progress in real-time within the Agnest desktop/web dashboard (`FR-M3-018`).
   - Provides live token telemetry, per-agent cost breakdown, and rapid operational controls: **Pause**, **Resume**, **Force Finalize ADR**, or **Override**.
   - Input entered in the Agnest dashboard is automatically synchronized and posted to the remote Forgejo Issue thread by the Control Plane to maintain complete historical transparency on Git.

---

## 5. Domain Entities & Data Model Extensions

### 5.1 `ENT-ExternalAgentIdentity` (MVP2)
Maps an internal `Agent` (`ENT-Agent`) to a remote Git provider persona:
- `id`: UUID (canonical Agnest ID)
- `agent_id`: Reference to `ENT-Agent`
- `provider_type`: `FORGEJO` | `GITHUB`
- `remote_username`: e.g. `agnest-implementer`
- `remote_email`: e.g. `agnest-implementer@agnest.local`
- `credential_ref`: Reference to `ENT-IntegrationCredentialRef` (stored in Secret Broker)
- `display_title`: e.g. "Agnest Software Implementer"
- `status`: `ACTIVE` | `SUSPENDED` | `REVOKED`

### 5.2 `ENT-RemoteReviewVerdict` (MVP4)
Represents a specialist agent's review submission projected to a remote PR:
- `id`: UUID
- `review_run_id`: Reference to `ENT-ReviewRun`
- `pull_request_id`: Reference to `ENT-PullRequest`
- `reviewer_identity_id`: Reference to `ENT-ExternalAgentIdentity`
- `verdict`: `APPROVE` | `REQUEST_CHANGES` | `COMMENT`
- `summary_body`: Markdown summary of findings
- `inline_comments`: Array of `{ path, line, side, body, finding_ref }`
- `remote_review_id`: External ID returned by Forgejo/GitHub API
- `submitted_at`: Timestamp

---

## 6. Functional Requirements Matrix

| ID | Requirement | Description | Target MVP |
|---|---|---|---|
| `FR-M2-019` | **External Identity Binding** | Agents can be bound to external provider identities (`ENT-ExternalAgentIdentity`) with secure credential references. | MVP2 |
| `FR-M4-021` | **Remote Review Projection** | Internal `ReviewFinding` and `ReviewRun` verdicts project to native Forgejo/GitHub PR reviews with file/line inline comments and formal verdicts. | MVP4 |
| `FR-M4-022` | **Agent PR Attribution** | Published branches and Pull Requests reflect the task's assigned agent remote identity as author. | MVP4 |
| `FR-M7-021` | **Multi-Identity Git Provider** | `GitProvider` interface supports executing API operations on behalf of specific agent identities while maintaining broker-managed credential isolation. | MVP7 |

---

## 7. Operational & Security Governance

1. **Least-Privilege Scoping:** Each agent token is scoped strictly to its function (e.g. Security reviewer account cannot push code to protected branches).
2. **Auditability & Provenance:** Every remote API interaction records:
   - Requesting agent ID and runtime model.
   - Associated Agnest task ID and workspace commit SHA.
   - Remote response ID and HTTP status.
3. **Rate Limiting & Anti-Loop Safeguards:** Control plane throttles remote comment frequency and terminates repetitive review loops if agents fail to converge within configured budgets (`FR-M3-016`).
