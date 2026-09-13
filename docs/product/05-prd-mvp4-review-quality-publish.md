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
