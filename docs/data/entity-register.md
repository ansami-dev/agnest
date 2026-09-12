# Entity Register

**Status:** Proposed — becomes binding when the bootstrap PR is merged.
**Owner:** Data Design. Amendments by PR; any role may propose one.
**Source:** `docs/product/COMPLETE-DOCUMENTATION.md` §8 and each PRD §9.

---

## What this is, and what the glossary is

This file is the **exhaustive** catalogue: every entity named in the product
documentation, each with an `ENT-` ID allocated on sight, the MVP that introduces it,
and a one-line definition sufficient to tell it apart from its neighbours.

`docs/glossary.md` is the **conceptual** companion. It covers fewer terms, at more
length, and leads with the distinctions two roles will otherwise blur. Where the two
files overlap, the glossary is the fuller treatment and this file is the index.

An entity appearing here is not a commitment to a table. Some will become tables, some
columns, some value objects, some event payload fields. Modelling decisions land in
`docs/data/entities-M<n>.md` and cite the `ENT-` ID allocated here.

## Rules

1. **`ENT-` IDs are allocated here and only here.** `ENT-<PascalName>` is name-derived
   rather than sequential, so two roles working in parallel cannot collide on one
   (see `docs/agents/roles.md` §4.1).
   **Event types do not belong here.** `EVT-` IDs are allocated in
   `docs/data/event-register.md`. An entity is a thing that exists; an event is a thing
   that happened. If an entry is named for something that occurred at a point in time, it
   is an event and belongs in the other register.
2. **Renaming an entity allocates a new ID.** The old row stays, marked superseded, so
   documents that cited it remain readable.
3. **A name used in any Agnest document must appear here or in the glossary.** A name in
   neither is a name two people are using differently.
4. "Introduced in" is the MVP that first requires the concept, not the MVP where it
   stops changing.

---

## MVP1 — Git Foundation & Sandboxed Workspaces

| ID | Entity | Definition |
|---|---|---|
| `ENT-Project` | **Project** | Logical software product or codebase context. May hold several repositories, agents, groups, workflows, policy profiles. Gains tenant ownership in M8. |
| `ENT-Repository` | **Repository** | Git repository with remote metadata, mirror state, default branch, supported workflows, intelligence state. |
| `ENT-RepositoryRemote` | **RepositoryRemote** | Remote endpoint and integration identity for a Repository. Separated from Repository so one repository may later carry several remotes. |
| `ENT-RepositoryFetchState` | **RepositoryFetchState** | Last successful fetch: commit, timestamp, outcome, and error if any. Distinct from Repository so a failed fetch never mutates repository identity. |
| `ENT-Workspace` | **Workspace** | Task-scoped local worktree plus execution metadata: branch, pinned base SHA, status, lifecycle state. Primary engineering working state. |
| `ENT-WorkspaceBranch` | **WorkspaceBranch** | Branch created for a Workspace under the configured naming convention. Carries the local branch name and whether it has ever been published. |
| `ENT-Sandbox` | **Sandbox** | Compute boundary hosting a harness with the Workspace attached. Ephemeral; may be destroyed without destroying its Workspace. |
| `ENT-SandboxProvider` | **SandboxProvider** | An implementation of the sandbox contract (Docker, LXC, VM) that declares its capabilities rather than pretending uniformity. |
| `ENT-CommandRun` | **CommandRun** | One command executed in a Sandbox: stdout, stderr, exit code, timestamps, timeout. Large output is stored as a blob reference, not a row. |
| `ENT-TestRun` | **TestRun** | A named test command execution and its persisted result. Bound to a workspace revision so it can become stale. |
| `ENT-WorkspaceChangeSummary` | **WorkspaceChangeSummary** | Derived summary of the Workspace's current Git status: files modified, added, deleted, renamed, staged, untracked, plus diff size. |
| `ENT-Issue` | **Issue** | Engineering work item imported from Forgejo/GitHub or created locally. Human-facing, no runtime. Introduced in the vision domain model. |

---

## MVP2 — Agent Runtime Fabric

| ID | Entity | Definition |
|---|---|---|
| `ENT-Agent` | **Agent** | Persistent identity independent of harness, model, and sandbox: role, capabilities, permissions, policy, history references, group memberships. |
| `ENT-AgentRole` | **AgentRole** | Named role such as Implementer, QA, Code Review, Security, Architect. Drives context policy and permission defaults. |
| `ENT-Capability` | **Capability** | A declared ability, held by an Agent (what it is for) and separately by a harness (what it can technically do). |
| `ENT-RuntimeAdapterType` | **RuntimeAdapterType** | The adapter kind for a harness: Hermes, Claude Code, Codex, OMP. The extension point for a fifth harness. |
| `ENT-RuntimeBinding` | **RuntimeBinding** | Task-scoped binding of Agent + harness + model/provider config + Sandbox + Workspace + Task. Never permanent. |
| `ENT-RuntimeSession` | **RuntimeSession** | The harness's own session. May be resumable. Never the durable source of task state. |
| `ENT-RuntimeCapabilitySnapshot` | **RuntimeCapabilitySnapshot** | What the harness reported it could do, at a version, at a moment. Stored for reproducibility; capability is version-aware. |
| `ENT-AgentExecution` | **AgentExecution** | One execution of one Task by one Agent through one RuntimeBinding. The unit telemetry and cost attach to. |
| `ENT-RuntimeEvent` | **RuntimeEvent** | A normalized activity event emitted by an adapter. Typed where the harness offers structure, raw text only as fallback. |
| `ENT-ArtifactReference` | **ArtifactReference** | A pointer from an execution to an Artifact, so runtime output enters durable state without the transcript doing so. |
| `ENT-ModelExecutionMetadata` | **ModelExecutionMetadata** | Actual model and provider used, where knowable. Recorded without product logic depending on it (P3). |

---

## MVP3 — Multi-Agent Orchestration & Groups

| ID | Entity | Definition |
|---|---|---|
| `ENT-Task` | **Task** | Executable unit of work assigned to an Agent or Group: lifecycle, owner, dependencies, inputs, artifacts, workspace and context references, outcome. |
| `ENT-TaskDependency` | **TaskDependency** | A prerequisite edge between Tasks, with the policy that decides when the dependency is satisfied. |
| `ENT-TaskAssignment` | **TaskAssignment** | Assignment of a Task to an Agent or Group, with actor and timestamp. Separate from Task so reassignment keeps history. |
| `ENT-Group` | **Group** | Agents operating in deliberation or workflow mode with explicit coordination, context, artifact, and termination policies. |
| `ENT-GroupMember` | **GroupMember** | Membership of an Agent in a Group, with its role in that group. |
| `ENT-GroupPolicy` | **GroupPolicy** | Rounds, budget, activation, turn-taking, context visibility, and termination rules for a Group. |
| `ENT-WorkflowTemplate` | **WorkflowTemplate** | A reusable Group or workflow definition. Separate from WorkflowRun so editing a template never rewrites history. |
| `ENT-WorkflowRun` | **WorkflowRun** | One execution of a WorkflowTemplate, pinned to the template version it started from. |
| `ENT-WorkflowStage` | **WorkflowStage** | One step in a WorkflowRun, with completion criteria and retry/rework transitions. |
| `ENT-Artifact` | **Artifact** | Durable typed output. Immutable and versioned, or explicitly superseded. Never edited in place. |
| `ENT-ArtifactVersion` | **ArtifactVersion** | One immutable version of an Artifact. Supersession is recorded, not overwritten. |
| `ENT-Finding` | **Finding** | Artifact subtype carrying severity, status, and a reference to its subject. Produced by review. |
| `ENT-Decision` | **Decision** | Artifact subtype recording a choice, its rationale, and its unresolved questions. |
| `ENT-ApprovalRequest` | **ApprovalRequest** | A request for a human or policy gate on a protected transition: subject, action, risk context. |
| `ENT-ApprovalDecision` | **ApprovalDecision** | The answer to an ApprovalRequest: decision, actor, timestamp. Authenticated, immutable, auditable. |
| `ENT-Event` | **Event** | Typed record with a globally unique ID, causation and correlation IDs, actor, timestamp, and payload version. |
| `ENT-RetryAttempt` | **RetryAttempt** | One retry of a Task, distinguishing infrastructure or runtime failure from domain rejection. |
| `ENT-Handoff` | **Handoff** | The passing of artifact references from one WorkflowStage to the next. |

---

## MVP4 — Review, Quality Gates & Controlled Publish

| ID | Entity | Definition |
|---|---|---|
| `ENT-ReviewRun` | **ReviewRun** | One review pass by a QA, Code Review, or Security agent over a workspace revision. |
| `ENT-ReviewFinding` | **ReviewFinding** | A finding from a ReviewRun: verdict contribution, severity, affected source references, requested change. |
| `ENT-ReviewAnchor` | **ReviewAnchor** | The file, path, hunk, or line a finding attaches to, plus the source version. Anchors go stale and say so. |
| `ENT-QualityGate` | **QualityGate** | A policy over tests, review verdicts, unresolved findings, and required approvals. |
| `ENT-QualityGateEvaluation` | **QualityGateEvaluation** | A versioned snapshot of one gate evaluation. Never a mutable boolean. |
| `ENT-CommitIntent` | **CommitIntent** | The staged intent to commit: selected changes, message, author and committer metadata policy. |
| `ENT-CommitRecord` | **CommitRecord** | A local commit that happened: resulting SHA, actor, agent and model provenance. |
| `ENT-PublishRequest` | **PublishRequest** | The request to push a local branch through the control-plane Git credential. |
| `ENT-PublishResult` | **PublishResult** | The outcome of a PublishRequest: remote SHA, remote branch state, or the failure and its class. |
| `ENT-RemoteBranchState` | **RemoteBranchState** | Tracked remote state: unpublished, published, PR open, updated after publish, behind, ahead, diverged. |
| `ENT-PullRequest` | **PullRequest** | A PR on Forgejo or GitHub: remote URL, ID, status, and its relation to the local Task and Workspace. |
| `ENT-CIStatus` | **CIStatus** | A check or status result from the remote, correlated to a commit and thereby to a Task. |
| `ENT-RiskAcceptance` | **RiskAcceptance** | A recorded, privileged waiver of a finding, with actor and reason. Immutable. |

---

## MVP5 — Repository Intelligence

| ID | Entity | Definition |
|---|---|---|
| `ENT-RepositoryIndex` | **RepositoryIndex** | The derived intelligence state for a Repository. Rebuildable, never canonical. |
| `ENT-IndexGeneration` | **IndexGeneration** | A version of the index. What staleness is measured against and what makes retrieval reproducible. |
| `ENT-SourceFile` | **SourceFile** | An indexed file: path, language, parse status. Unsupported files remain lexically searchable. |
| `ENT-Symbol` | **Symbol** | An extracted code entity: module, class, function, method, interface, type, constant. |
| `ENT-Relationship` | **Relationship** | An extracted edge: contains, imports, calls, references, extends, implements, tests, depends-on. |
| `ENT-RelationshipProvenance` | **RelationshipProvenance** | How a Relationship was extracted and how far it can be trusted: method, confidence, source location. |
| `ENT-LexicalDocument` | **LexicalDocument** | A unit in the lexical index, tuned for identifiers, error strings, API names, and config keys. |
| `ENT-EmbeddingRecord` | **EmbeddingRecord** | A stored embedding, or a reference to one held in an external vector backend. |
| `ENT-GitHistoryFact` | **GitHistoryFact** | A history signal: recent commits touching a candidate, changed-together pairs, blame metadata. |
| `ENT-TestAssociation` | **TestAssociation** | A link from a test to the module or symbol it exercises, by static relation or by history heuristic. |
| `ENT-DocReference` | **DocReference** | A link from indexed documentation, ADRs, or issues to the code they describe. |
| `ENT-WorkspaceIndexOverlay` | **WorkspaceIndexOverlay** | A Workspace's changes layered over the immutable base index, so reviewers query current task state. |
| `ENT-RetrievalQuery` | **RetrievalQuery** | One query against the intelligence API, with its intent classification. |
| `ENT-RetrievalCandidate` | **RetrievalCandidate** | One scored result: source reference, match explanation, provenance, confidence. |

---

## MVP6 — Context Intelligence & Token Economics

| ID | Entity | Definition |
|---|---|---|
| `ENT-ContextRequest` | **ContextRequest** | A request for context: task, agent role, objective, workspace revision, budget, retrieval policy. |
| `ENT-ContextPolicy` | **ContextPolicy** | Versioned, declarative rules governing retrieval and budget allocation. |
| `ENT-RoleContextProfile` | **RoleContextProfile** | The context profile for one role, group, or workflow stage. |
| `ENT-RetrievalPlan` | **RetrievalPlan** | The queries and intents derived from a ContextRequest before anything is retrieved. |
| `ENT-RetrievalRun` | **RetrievalRun** | One execution of a RetrievalPlan, with per-source latency and candidate counts. |
| `ENT-ContextCandidate` | **ContextCandidate** | One retrieved item before selection, with its score and source. |
| `ENT-ContextSelection` | **ContextSelection** | What survived fusion, rerank, dedup, and budget, and what was dropped and why. |
| `ENT-ContextPack` | **ContextPack** | Immutable versioned package of instructions, evidence, source references, recorded omissions, budget, generation metadata. |
| `ENT-ContextPackItem` | **ContextPackItem** | One item in a pack, typed as source, derived, artifact, or instruction, and carrying its provenance. |
| `ENT-ContextEscalation` | **ContextEscalation** | A runtime's request for more context, with reason and category. Never broadens access beyond the agent's scope. |
| `ENT-TokenUsage` | **TokenUsage** | Tokens by stage: requested, retrieved, selected, sent, output, cached, compressed. |
| `ENT-CostRecord` | **CostRecord** | Cost for an execution or task, derived from usage and configured provider rates. |
| `ENT-CompressionRecord` | **CompressionRecord** | What an optional compressor did, and to what. Provenance survives compression. |
| `ENT-QualityOutcome` | **QualityOutcome** | Test, review, and task results associated with the context pack that produced them. |
| `ENT-ContextBenchmarkRun` | **ContextBenchmarkRun** | A benchmark comparing baseline harness-only execution against context-assisted execution on the same issues. |

---

## MVP7 — Integrations & Inference Fabric

| ID | Entity | Definition |
|---|---|---|
| `ENT-Integration` | **Integration** | A configured external system: Git host, CI, MCP server, inference provider. |
| `ENT-IntegrationCredentialRef` | **IntegrationCredentialRef** | A reference to a credential. What is stored in configuration. Never a plaintext value. |
| `ENT-ProviderCapability` | **ProviderCapability** | What a provider declares it supports, versioned and discoverable. |
| `ENT-MCPServer` | **MCPServer** | A registered tool endpoint: transport, capabilities, credential reference, health, allowed roles and projects. |
| `ENT-MCPTool` | **MCPTool** | One tool exposed by an MCPServer. Never inherited by default. |
| `ENT-ToolPolicy` | **ToolPolicy** | Allow and deny rules for tools, per agent, task, or group. Deny by default. |
| `ENT-InferenceProvider` | **InferenceProvider** | A model endpoint: direct cloud provider, local OpenAI-compatible server, or gateway. |
| `ENT-ModelDescriptor` | **ModelDescriptor** | Provider plus canonical provider model ID. Routing aliases are policy, not identity. |
| `ENT-ModelPolicy` | **ModelPolicy** | Role or task defaults, required capabilities, max cost and context, preferred and fallback models. |
| `ENT-InferenceRoute` | **InferenceRoute** | The resolved path for a model call under a ModelPolicy. |
| `ENT-InferenceAttempt` | **InferenceAttempt** | One try along a route, including each fallback, with its outcome class. |
| `ENT-UsageRecord` | **UsageRecord** | Normalized usage for one attempt, preserving the raw provider metrics alongside. |
| `ENT-QuotaSnapshot` | **QuotaSnapshot** | A point-in-time quota or rate-limit hint from a provider. A hint, not a guarantee. |
| `ENT-CIProvider` | **CIProvider** | An adapter for a CI system: status and check ingestion, and rerun or cancel where supported. |
| `ENT-ExternalWebhookEvent` | **ExternalWebhookEvent** | A received external event, authenticated and deduplicated before it becomes an internal Event. |

---

## MVP8 — Governance, Enterprise Security & Scale

| ID | Entity | Definition |
|---|---|---|
| `ENT-Organization` | **Organization** | Top-level tenant. Owns teams, projects, budgets, and policy. |
| `ENT-Team` | **Team** | A grouping within an Organization that memberships and permissions attach to. |
| `ENT-Membership` | **Membership** | A principal's membership in an Organization or Team, with its role. |
| `ENT-Role` | **Role** | A named permission set: admin, developer, reviewer, security, auditor, operator, or custom. |
| `ENT-Permission` | **Permission** | One authorization over one resource kind and action. |
| `ENT-Policy` | **Policy** | Conditions over repository classification, task type, agent role, sandbox class, provider trust, action type, finding severity. |
| `ENT-PolicyVersion` | **PolicyVersion** | An immutable version of a Policy, so a past decision can still be explained. |
| `ENT-PolicyDecision` | **PolicyDecision** | A versioned, explainable allow or deny, referenced by the protected action it governed. |
| `ENT-ResourceClassification` | **ResourceClassification** | The sensitivity label on a repository or project that policy conditions read. |
| `ENT-SecretRef` | **SecretRef** | A reference to a secret. What configuration and task definitions hold. |
| `ENT-SecretLease` | **SecretLease** | A scoped short-lived grant of an actual secret value, with expiry and revocation. |
| `ENT-Budget` | **Budget** | A spend limit at organization, project, user, or agent scope. |
| `ENT-Quota` | **Quota** | A non-monetary limit: concurrency, workspaces, sandbox resources. |
| `ENT-UsageAggregate` | **UsageAggregate** | Rolled-up usage for budget evaluation and reporting, along declared dimensions. |
| `ENT-AuditEvent` | **AuditEvent** | An immutable append-oriented record of a security, engineering, or control action. Never contains a secret value. |
| `ENT-RetentionPolicy` | **RetentionPolicy** | How long workspaces, logs, transcripts, context packs, artifacts, indexes, and usage records are kept. |
| `ENT-DeletionJob` | **DeletionJob** | An authorized deletion, including derived intelligence where required, with its completion evidence. |
| `ENT-WorkerNode` | **WorkerNode** | A distributed worker that executes tasks, with an authenticated control channel identity. |
| `ENT-WorkerCapability` | **WorkerCapability** | What a WorkerNode can host, which placement reads. |
| `ENT-PlacementDecision` | **PlacementDecision** | Why a task landed on a given worker, retained so scheduling is explainable. |
| `ENT-SecurityAlert` | **SecurityAlert** | A raised condition: credential failure, denied action, unusual spend, sandbox policy violation, repeated publish failure. |
| `ENT-BackupRecord` | **BackupRecord** | A backup and what it covers, so a restore can be reasoned about against the documented RPO. |

---

## Count

120 entities across 8 MVPs. Every entity named in PRD §9 of every MVP, plus `Issue`
from the vision domain model §8, is present.

One naming note, so the count is verifiable rather than asserted: PRD MVP5 §9 writes
`EmbeddingRecord/Reference` as a single item, meaning the record or a reference to one
held externally. It is modelled here as `ENT-EmbeddingRecord`, whose definition covers
both. A word-splitting check over the PRD will report `Reference` as unmatched; that is
the splitter, not a gap.
