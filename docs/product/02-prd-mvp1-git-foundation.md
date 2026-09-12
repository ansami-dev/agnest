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
