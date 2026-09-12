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

- **FR-M7-001 GitProvider interface:** repo metadata, issue/PR, branch, status/checks, webhooks, comments as supported.
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
