# Agnest Glossary

**Status:** Proposed — becomes binding when the bootstrap PR is merged.
**Owner:** Data Design. Amendments by PR; any role may propose one.
**Source:** `docs/product/COMPLETE-DOCUMENTATION.md` §8 (core domain model) and the
per-MVP entity lists in each PRD §9.

---

## How to use this file, and how it relates to the entity register

This file is the **conceptual** reference: the terms whose meaning two roles will
otherwise blur, treated at enough length to settle the ambiguity. It is deliberately not
exhaustive.

`docs/data/entity-register.md` is the **exhaustive** catalogue of things that exist —
every entity named anywhere in the product documentation, with its `ENT-` ID and a
one-line definition. `docs/data/event-register.md` is the same for things that happened,
carrying `EVT-` IDs. Where any of them overlap this file, this file is the fuller
treatment and the registers are the index.

A name used in any Agnest document must appear in one of the three. A name in neither is a
name two people are using differently. If a document needs a term neither file defines,
it is added in the same PR that first uses it.

Conventions:

- Entity names are written in `PascalCase` when referring to the modelled entity
  (`Workspace`), and in plain lowercase when referring to the everyday idea
  ("the workspace directory on disk").
- Entities carry `ENT-` IDs (see `docs/agents/roles.md` §4). The ID is listed beside
  each entity below once that entity has been modelled.
- "Introduced in" is the MVP that first requires the concept, not the MVP where it stops
  changing.

---

## 1. The distinctions that will drift

These are the pairs where two roles will use the same word for different things unless
we are deliberate. Read this section even if you skip the rest.

### Issue vs Task

| | |
|---|---|
| **Issue** | An engineering work item, imported from Forgejo/GitHub or created locally. Human-facing. Has no runtime. |
| **Task** | An **executable** unit of work assigned to an Agent or Group. Has lifecycle, dependencies, inputs, artifacts, workspace and context references, and an outcome. |

One Issue may produce many Tasks. A Task may exist with no Issue behind it. Never use
"issue" to mean an assigned unit of agent work.

### Workspace vs Worktree

| | |
|---|---|
| **Workspace** | The product entity: a task-scoped local Git worktree **plus** its execution metadata — branch, pinned base commit SHA, status, lifecycle state, sandbox attachment. This is the primary engineering working state. |
| **Worktree** | The Git mechanism the Workspace is built on. An implementation detail of the Workspace. |

Product documents say Workspace. Say "worktree" only when discussing Git mechanics.

### Workspace vs Sandbox

| | |
|---|---|
| **Workspace** | Filesystem and Git state. Durable; may outlive any sandbox. |
| **Sandbox** | The ephemeral compute boundary hosting a harness and having the Workspace attached. MVP1 uses a local Incus instance; future backends require a separate decision. |

A Sandbox attaches to a Workspace; they are not two names for one thing. **Sandbox IDs
are provider-scoped and must never become stable product identity** (MVP1 §9).
Destroying a Sandbox does not destroy its Workspace.

### Agent vs Harness vs Runtime Adapter vs Runtime Binding vs Runtime Session vs Model

The whole point of MVP2 is that these are six different things.

| Term | Lifetime | Meaning |
|---|---|---|
| **Agent** | Long-lived | Persistent identity: role, capabilities, permissions, policy, history references, group memberships. Independent of harness, model, and sandbox. |
| **Harness** | — | A concrete coding runtime: Hermes, Claude Code, Codex, OMP. |
| **Runtime Adapter** | — | The anti-corruption layer translating between the product domain and one harness's session semantics. One adapter per harness. |
| **Runtime Binding** | Task/session-scoped | The concrete binding of Agent + harness + model/provider config + Sandbox + Workspace + Task. |
| **Runtime Session** | Harness-side | The harness's own session. May be resumable. **Never the durable source of task state.** |
| **Agent Execution** | One run | One execution of one Task by one Agent through one Runtime Binding. |

`Agent != Harness`, `Agent != Sandbox`, `Agent != Model` (principles P1–P3). Changing
the runtime must not create a new Agent record (`FR-M2-016`).

### Entity vs Event

| | |
|---|---|
| **Entity** | A thing that exists. Has a current state, is updated in place, and is migrated when its shape changes. Catalogued in `docs/data/entity-register.md` as `ENT-<PascalName>`. |
| **Event** | A thing that happened. Immutable once written, never updated, and versioned by payload rather than migrated. Catalogued in `docs/data/event-register.md` as `EVT-<PascalName>`. |

`ENT-Workspace` is the workspace; `EVT-WorkspaceDiscarded` is the moment one was thrown
away. Two registers, because the identity, retention, and versioning rules genuinely
differ — and because MVP3's recovery story depends on events being replayable, which
requires that nothing ever edits one.

### Artifact vs Finding vs Decision vs Approval vs Handoff

| | |
|---|---|
| **Artifact** | Any durable typed output. Immutable and versioned, or explicitly superseded. The general case. |
| **Finding** | An Artifact subtype carrying severity, status, and a reference to the subject it is about. Produced by review. |
| **Decision** | An Artifact subtype recording a choice, its rationale, and unresolved questions. |
| **Approval** | Not an Artifact. A gate: an `ApprovalRequest` and its `ApprovalDecision`, authenticated, immutable, auditable. |
| **Handoff** | The passing of artifact references from one workflow stage to the next. |

### Commit vs Publish vs Pull Request vs Merge

Four separate state transitions, four separate authorizations. Collapsing any two of
them is a security defect, not a wording slip.

| | |
|---|---|
| **Commit** | Create a local commit in the Workspace. No remote contact. |
| **Publish** | Push a local branch to the remote, **through the control plane's Git credential** — never the agent sandbox's. |
| **Pull Request** | Create a PR on Forgejo/GitHub after Publish. |
| **Merge** | Remote merge. Out of scope for autonomous action. |

Do not write "push" when you mean Publish. "Push" is the Git verb; Publish is the
governed product action that happens to use it.

### Canonical vs Derived

| | |
|---|---|
| **Canonical** | Git source and selected repository artifacts. The truth. |
| **Derived** | Graph, embeddings, lexical index, summaries, memories. Rebuildable, cache-like, never authoritative over source. |

Principle P8. A derived store may accelerate investigation; it may never silently
replace reading the canonical source.

---

## 2. Project and repository

| Term | Introduced | Definition |
|---|---|---|
| **Project** | MVP1 | A logical software product or codebase context. May contain several repositories, agents, groups, workflows, and policy profiles. Gains tenant ownership in MVP8. |
| **Repository** | MVP1 | A Git repository with remote metadata, mirror/cache state, default branch, supported workflows, and repository intelligence state. |
| **Repository Remote** | MVP1 | The remote endpoint and integration identity for a Repository. |
| **Mirror** | MVP1 | The local bare Git object store used to create worktrees efficiently without repeated full clones. |
| **Base Commit** | MVP1 | The exact commit SHA a Workspace was created from. Pinned and immutable for that Workspace (`FR-M1-004`). |
| **Workspace Revision** | MVP1 | A deterministic identifier for the exact tracked, staged, and untracked working-tree state a status, diff, command, test, or later review was produced against. It is not the `HEAD` commit SHA. Used to detect staleness. |

## 3. Execution

| Term | Introduced | Definition |
|---|---|---|
| **Sandbox Provider** | MVP1 | An implementation behind the sandbox contract. MVP1 implements local Incus only and treats system container, OCI application container, and VM as separately evidenced instance kinds rather than pretending uniformity. |
| **Command Run** | MVP1 | One command executed in a Sandbox, with stdout, stderr, exit code, timestamps, and timeout. |
| **Test Run** | MVP1 | A named test command execution and its persisted result. |
| **Workspace Confinement** | MVP1 | The rule that sandbox filesystem writes are limited to the assigned Workspace plus explicitly configured ephemeral paths (`FR-M1-010`). |
| **Control Plane** | MVP1 | The trusted application process that authenticates operator intent, coordinates use cases, owns orchestration metadata, and calls privileged brokers only through typed ports (`ARC-M1-001`). |
| **Repository Service** | MVP1 | The control-plane component that owns repository metadata and serializes bare-mirror refresh operations without receiving a Git credential (`ARC-M1-002`). |
| **Git Workspace Service** | MVP1 | The host-side component that owns Workspace paths and performs local Git worktree, status, diff, stage, restore, quarantine, discard, and archive operations (`ARC-M1-003`). |
| **Credentialed-Fetch Broker** | MVP1 | A separate least-authority process that holds a host-bound fetch credential and executes sanitized fetch into an approved bare mirror (`ARC-M1-004`). |
| **Sandbox-Provider Broker** | MVP1 | A separate high-authority process that alone holds provider-daemon access and resolves server-owned confinement profiles (`ARC-M1-005`). |
| **Execution Gateway** | MVP1 | The control-plane component that validates and audits bounded execution requests and dispatches them to an existing Sandbox generation (`ARC-M1-006`). |
| **Recovery Reconciler** | MVP1 | The control-plane component that compares durable intent with attributed provider/filesystem observations and recovers through normal policy-enforcing ports (`ARC-M1-007`). |
| **Task Sandbox** | MVP1 | The untrusted execution boundary for one assigned Workspace projection; it has no access to shared Git administration, broker IPC, provider authority, or control-plane credentials (`ARC-M1-008`). |

## 4. Orchestration

| Term | Introduced | Definition |
|---|---|---|
| **Group** | MVP3 | A collection of Agents operating in deliberation or workflow mode, with explicit coordination, context, artifact, and termination policies. |
| **Deliberation Group** | MVP3 | Several agents reasoning about the same problem, producing a decision, recommendation, or review. |
| **Workflow Group** | MVP3 | Agents owning different delivery stages, passing durable artifacts between them. |
| **Coordinator** | MVP3 | A role and policy within a group, not a permanent special agent. |
| **Stage** | MVP3 | One step in a Workflow Group, with completion criteria and retry/rework transitions. |
| **Event** | MVP3 | A typed, globally-identified record with causation and correlation IDs, actor, timestamp, and payload version. |
| **Protected Action** | MVP4 | An action requiring explicit authorization and audit: commit, publish, PR, merge, secret access, expanded network access, model escalation. |
| **Quality Gate** | MVP4 | A policy evaluation over tests, review verdicts, unresolved findings, and required approvals. Evaluations are versioned snapshots, never a mutable boolean. |
| **Risk Acceptance** | MVP4 | A recorded, privileged waiver of a finding, with actor and reason. |

## 5. Intelligence and context

| Term | Introduced | Definition |
|---|---|---|
| **Repository Index** | MVP5 | The derived intelligence snapshot for a Repository at a commit. |
| **Index Generation** | MVP5 | A version of the index, used to detect staleness and to make retrieval reproducible. |
| **Symbol** | MVP5 | An extracted code entity: module, class, function, method, interface, type, constant. |
| **Relationship** | MVP5 | An extracted edge between symbols — contains, imports, calls, references, extends, implements, tests, depends-on — carrying provenance and confidence. |
| **Provenance** | MVP5 | The link from a retrieval result back to repository, commit or workspace revision, path, and line or symbol range. |
| **Confidence** | MVP5 | How much a derived relationship can be trusted. Derived edges are never asserted as fact. |
| **Workspace Overlay** | MVP5 | A representation of a Workspace's changes layered over the immutable base index, so reviewers query current task state rather than stale `main`. |
| **Context Pack** | MVP6 | An immutable, versioned package of instructions, evidence, source references, recorded omissions, budget, and generation metadata, assembled for one task execution. |
| **Context Tier** | MVP6 | The breadth level of retrieved evidence: summary/graph, snippets, full files, expanded module or repository scope. |
| **Context Escalation** | MVP6 | A runtime's request for more context, with a recorded reason and category. Escalation never broadens access beyond the agent's permission scope. |
| **Avoided Context** | MVP6 | Estimated available repository context minus context actually sent, under a published methodology. |

## 6. Integration and inference

| Term | Introduced | Definition |
|---|---|---|
| **Git Provider** | MVP7 | An adapter for a Git host: Forgejo, GitHub, future hosts. |
| **MCP Server / MCP Tool** | MVP7 | A registered tool endpoint and the individual tools it exposes, subject to per-agent, per-task, per-group policy. Never inherited by default. |
| **Inference Provider** | MVP7 | A model endpoint: direct cloud provider, local OpenAI-compatible server, or gateway. |
| **Model Descriptor** | MVP7 | Provider plus canonical provider model ID. **Routing aliases are policy objects, not model identity.** |
| **Inference Route / Attempt** | MVP7 | The resolved path for a model call, and each individual try including fallbacks. |
| **Provider Trust Tier** | MVP7 | A classification governing what task context a provider may receive, and whether fallback to it is permitted. |

## 7. Security and governance

| Term | Introduced | Definition |
|---|---|---|
| **Trust Zone** | MVP1 | One of the separated zones: user/browser, control plane, Git credential service, runtime adapter, sandbox, repository workspace, external model provider, MCP/tool server, remote Git provider, external CI/CD. |
| **Trust Boundary** | MVP1 | The crossing between two trust zones. Every crossing is where a control belongs. |
| **Secret Ref** | MVP7 | A reference to a secret. What is stored in configuration and task definitions. Never a plaintext value. |
| **Secret Lease** | MVP8 | A scoped, short-lived grant of an actual secret value, with expiry and revocation. |
| **Policy Decision** | MVP8 | A versioned, explainable allow/deny outcome, referenced by the protected action it governed. |
| **Tenant** | MVP8 | The ownership scope — Organization, Team, Project — that must be explicit in all primary data **and in every index**, not only in API records. |
| **Separation of Duties** | MVP8 | The requirement that the actor who requests a protected action is not the actor who approves it. |
| **Break-glass** | MVP8 | Emergency elevated access, permitted but subject to enhanced audit. |

---

## 8. Words we do not use

| Avoid | Use instead | Why |
|---|---|---|
| "push" (as a product action) | **Publish** | Publish is governed and credential-separated; push is the underlying Git verb |
| "worktree" (as the product entity) | **Workspace** | The Workspace is more than its worktree |
| "session" (for a unit of work) | **Agent Execution** or **Task** | Runtime Session is a harness-side concept and is not durable state |
| "the graph says" | "the index suggests, source confirms" | Derived data is never asserted over canonical source (P8) |
| "the agent's credentials" for remote Git | **control-plane Git credential** | The agent sandbox has none by default (P9) |
| "memory" unqualified | name the store: Context Pack, Artifact, harness-native memory | Three different things with three different retention rules |
| "approval" for an automated check | **Quality Gate** | Approval is a human or policy gate with an actor; a gate is an evaluation |
