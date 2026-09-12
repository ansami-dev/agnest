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

The initial runtime focus is **Hermes, Claude Code, Codex, and OMP**. The initial sandbox focus is **Docker, LXC, and VM**. The initial remote Git focus is **Forgejo and GitHub**. The protocol direction is **A2A for agent interoperability** and **MCP for tools/data access**, with adapters where runtimes do not natively implement those protocols.

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

Docker, LXC, VM, Kubernetes, remote machines, and future runtimes sit behind a common sandbox contract.

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

Persistent identity independent from runtime. Stores role, capabilities, permissions, policy, history references, and group memberships.

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
4. User or workflow assigns issue to an agent/group.
5. Control plane creates branch + worktree + workspace.
6. Sandbox provider provisions Docker/LXC/VM and attaches the workspace.
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
17. Git service commits/pushes using control-plane authority.
18. PR is created in Forgejo/GitHub.
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
3. **Sandbox-provider abstraction** — Docker/LXC/VM selected by policy.
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
10. What is the minimum portable sandbox contract that works across Docker, LXC, and VM without hiding critical capability differences?

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
