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
