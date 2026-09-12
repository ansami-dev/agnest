# PRD — MVP 5: Repository Intelligence

## 1. Purpose

Build a repository intelligence substrate that reduces blind exploration. Index source structure deterministically where possible, maintain symbol and relationship graphs, add lexical and semantic retrieval, enrich with Git/test/spec metadata, support workspace overlays, and return provenance-linked candidate scope for source verification.

## 2. Product Context

This MVP is part of the **Git-Native Multi-Agent Engineering Control Plane** roadmap. All requirements inherit the product principles: harness agnostic, sandbox agnostic, model agnostic, Git native, A2A native, artifact driven, context efficient, source verified, and local-first/remote-by-approval.

## 3. Goals

- Parse supported languages into files/symbols/relationships using deterministic tooling where feasible.
- Build queryable code relationship graph for imports, calls/references where available, inheritance/implementation, tests, dependencies.
- Add lexical/full-text retrieval optimized for identifiers, error strings, API names, config keys.
- Add vector/semantic retrieval for conceptual search.
- Fuse retrieval modes and expose a stable Repository Intelligence API.
- Track Git commit/version provenance and active workspace overlay.
- Support impact/blast-radius queries and candidate test discovery.
- Always provide source references so runtimes can read canonical code before edits.

## 4. Non-Goals

- Fully sound whole-program static analysis for every language.
- Guarantee that graph relationships are complete/correct enough to replace source reading.
- Autonomous code modification by intelligence service.
- Final role-aware context budgeting (MVP6).
- Cross-organization global knowledge graph.

## 5. Primary Users

- Solo AI-native developer running multiple coding agents.
- Engineering lead supervising AI implementation and review.
- Platform engineer operating sandbox/runtime infrastructure.
- Security engineer validating trust boundaries and remote publication authority.

## 6. Primary Workflows

### W1 — Index base repository
After fetch, platform indexes supported files, symbols, relationships, lexical terms, embeddings, and Git metadata for pinned commit.

### W2 — Issue exploration
Query `hub key rotation` returns lexical, semantic, and graph candidates with source paths/symbols and relevance evidence.

### W3 — Impact analysis
Given changed symbol, system returns likely callers, dependents, tests, API surfaces, and related specs with confidence/provenance.

### W4 — Workspace overlay
Agent modifies code in worktree. Intelligence updates/overlays changed symbols so reviewers query current workspace state instead of stale main.

## 7. Functional Requirements

- **FR-M5-001 Repository index job:** build/version intelligence snapshot for repository commit.
- **FR-M5-002 Language detection/parser registry:** identify supported languages and parser capability.
- **FR-M5-003 Symbol extraction:** files/modules/classes/functions/methods/interfaces/types/constants where parser supports.
- **FR-M5-004 Relationship extraction:** contains/imports/calls/references/extends/implements/tests/depends-on with provenance/confidence.
- **FR-M5-005 Lexical index:** identifier/path/content/error/config search with ranking.
- **FR-M5-006 Vector index:** embedding generation/storage/search with configurable model/backend.
- **FR-M5-007 Hybrid search API:** execute lexical + semantic + graph retrieval and return scored candidates.
- **FR-M5-008 Graph query API:** neighbors, shortest relevant path, callers/callees, import/dependency traversal, impacted tests.
- **FR-M5-009 Source provenance:** candidate links to repository, commit/workspace revision, path, line/symbol range where possible.
- **FR-M5-010 Git enrichment:** recent commits touching candidate, changed-together signals, blame/history metadata where configured.
- **FR-M5-011 Test mapping:** associate tests with modules/symbols through static relation and history heuristics.
- **FR-M5-012 Spec/doc linkage:** index selected Markdown/docs/ADRs/issues and link references to code where derivable.
- **FR-M5-013 Incremental indexing:** update changed files without mandatory full rebuild where backend supports reliable updates.
- **FR-M5-014 Workspace overlay:** represent task changes separately from immutable/base index.
- **FR-M5-015 Consistency check:** detect stale index vs repository/workspace revision.
- **FR-M5-016 Rebuild:** full rebuild path when incremental state is suspect.
- **FR-M5-017 Provider abstraction:** Graphify/other graph extractor and Neo4j/other backends are replaceable implementations.
- **FR-M5-018 Retrieval explanation:** return why candidate matched (lexical, semantic, graph relation, history, explicit reference).
- **FR-M5-019 Source fetch:** canonical file/symbol content can be retrieved by candidate reference.
- **FR-M5-020 Index health:** per repo/workspace status, parser failures, unsupported files, freshness.

## 8. Non-Functional Requirements

- Indexing must be asynchronous and not block normal Git operations.
- Base index is versioned by commit or explicit generation.
- Unsupported language/file must fail gracefully and remain searchable lexically where possible.
- Search latency target for warm repository: p95 <= 2s for normal interactive hybrid query excluding expensive external embedding generation.
- Incremental update must not silently claim freshness when failed.
- Embedding provider must be configurable/local-capable for privacy/cost.

## 9. Domain Entities and Data Considerations

Entities: `RepositoryIndex`, `IndexGeneration`, `SourceFile`, `Symbol`, `Relationship`, `RelationshipProvenance`, `LexicalDocument`, `EmbeddingRecord/Reference`, `GitHistoryFact`, `TestAssociation`, `DocReference`, `WorkspaceIndexOverlay`, `RetrievalQuery`, `RetrievalCandidate`.

Graph nodes/edges require stable logical identity strategy across commits while preserving version lineage. Derived relationships need confidence and extraction method. Do not store source content redundantly without retention/consistency plan.

## 10. Integration Requirements

- Parser/AST framework such as tree-sitter or equivalent.
- Optional Graphify integration as a repository graph extractor/exporter.
- Graph backend abstraction, with Neo4j a candidate due to graph/vector/full-text capabilities.
- Embedding provider abstraction supporting local OpenAI-compatible and cloud providers.
- Git history and workspace service.
- Issue/spec ingestion sources.

No single graph/vector technology is mandatory at product-contract level.

## 11. Security and Trust Requirements

- Repository source and embeddings may contain sensitive IP; support local-only indexing mode.
- Index backends must enforce project/repository isolation.
- Queries must not cross repositories/projects without explicit permission.
- Derived docs/embeddings follow source retention/access policy.
- Do not execute repository code during indexing unless explicitly sandboxed.
- Treat parser/indexer inputs as untrusted; resource-limit parsing.
- Source fetch honors workspace permissions.

## 12. Architecture Considerations and Constraints

- Separate extraction, storage, retrieval, and source-fetch interfaces.
- Canonical source remains Git/workspace; index is derived/cache-like and rebuildable.
- Workspace overlay design is critical; avoid mutating shared base graph for every task.
- Support capability-specific relationship accuracy rather than pretending complete call graph.
- Consider Reciprocal Rank Fusion or pluggable fusion, but keep algorithm configurable.
- Design provenance as first-class to support later context verification.

## 13. Observability and Telemetry

Capture index duration, files/symbols/edges, unsupported parser rate, extraction errors, incremental update time, index freshness lag, lexical/vector/graph query latency, result counts, source fetches, rebuild frequency, storage size, embedding token/cost.

## 14. Acceptance Criteria

- Index a representative mixed-language repository and enumerate symbols/relationships with provenance.
- Exact identifier query returns correct symbol through lexical search.
- Conceptual query returns relevant files/symbols through vector search.
- Graph query finds direct dependents and likely tests for a changed symbol.
- Hybrid query returns ranked candidates with match explanation.
- Modify workspace file and show overlay query differs from base repository query.
- Simulate failed incremental index and show stale/failed health rather than incorrect `fresh` state.
- Rebuild index from source and reproduce usable retrieval state.
- Runtime can use candidate reference to read actual source before modification.

## 15. Dependencies

MVP1 repository/workspace source access; artifact storage; background job processing; optional embedding/model access; graph/vector/lexical backend selection.

## 16. Risks and Mitigations

- **Graph inaccuracies:** confidence/provenance, source verification, rebuild path.
- **Incremental index corruption:** generation IDs, overlay isolation, health checks.
- **Embedding cost/privacy:** configurable local models and selective indexing.
- **Language coverage gaps:** parser registry and lexical fallback.
- **Storage growth:** index retention/compaction and version policy.

## 17. Open Questions

1. Which languages are Tier-1 for deterministic graph support?
2. Should base graph be per default branch head, per commit, or rolling generation with source SHA references?
3. How are deleted/renamed symbols tracked across commits?
4. Which fusion algorithm is default and how is it evaluated?
5. How much Git history is indexed by default?
6. Should docs/specs share same graph or separate linked indexes?

## 18. Handoff — Architect Agent

Design intelligence service boundaries, parser/extractor pipeline, graph/lexical/vector backend contracts, index generation/versioning, workspace overlay architecture, rebuild/incremental strategy, retrieval API, provenance model, and scale characteristics. Evaluate Graphify+Neo4j as one implementation but keep interfaces replaceable.

## 19. Handoff — Security Agent

Define repository/index isolation, IP/privacy handling, local-only mode, parser sandbox/resource limits, backend access control, embedding-provider data exposure policy, source-fetch authorization, and retention/deletion requirements.

## 20. Handoff — Integration Agent

Specify contracts for parser registry, Graphify optional adapter, graph store, lexical store, vector/embedding providers, Git history ingestion, issue/spec sources, and source retrieval. Document failure/fallback behavior when one retrieval backend is unavailable.

## 21. Handoff — Data Design Agent

Define versioned schemas/IDs for files/symbols/relationships, provenance/confidence, index generations, embeddings, lexical docs, history facts, workspace overlays, retrieval candidates, and stale/fresh states. Propose logical identity across commits and deletion/rename lineage.
