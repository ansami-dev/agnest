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
