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
