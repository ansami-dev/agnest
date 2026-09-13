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
