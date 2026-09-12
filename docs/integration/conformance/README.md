# MVP1 integration conformance suite

**Status:** Proposed
**Owner:** Integration (Codex)
**Issue:** #9

[`cases-M1.json`](cases-M1.json) is the provider-neutral catalogue. An implementation
binds each case to a disposable provider fixture and emits the case ID, adapter version,
provider version, capability snapshot ID, result, duration, and sanitized evidence.

Cases listing `incus` run separately for `SYSTEM_CONTAINER`,
`OCI_APPLICATION_CONTAINER`, and `VM`. System-container cases are mandatory. An optional
kind may be reported unsupported, but if advertised it must pass every applicable case;
one kind's pass is never reused for another. Other sandbox providers are outside MVP1.

## Traceability

| Cases | Contract | Requirements | Architecture invariants |
|---|---|---|---|
| `CONF-M1-001`–`003`, `033` | `INT-M1-001` | `FR-M1-002`, `FR-M1-004`, `FR-M1-018` | `M1-I02`, `M1-I06`, `M1-I16` |
| `CONF-M1-004`–`007`, `033` | `INT-M1-002` | `FR-M1-002`, `FR-M1-003`, `FR-M1-017`, `FR-M1-018` | `M1-I02`, `M1-I05`, `M1-I06`, `M1-I09`, `M1-I16`–`M1-I18` |
| `CONF-M1-008`–`012` | `INT-M1-003` | `FR-M1-003`–`FR-M1-005`, `FR-M1-013`–`FR-M1-015`, `FR-M1-018`, `FR-M1-019` | `M1-I05`–`M1-I10`, `M1-I16`, `M1-I18`, `M1-I23` |
| `CONF-M1-013`–`018` | `INT-M1-004` | `FR-M1-005`–`FR-M1-010`, `FR-M1-016`, `FR-M1-019` | `M1-I03`, `M1-I07`, `M1-I08`, `M1-I11`–`M1-I13`, `M1-I16`–`M1-I18`, `M1-I22`, `M1-I23`, `M1-I25` |
| `CONF-M1-019`–`025`, `034`–`036` | `INT-M1-005` | `FR-M1-006`, `FR-M1-011`, `FR-M1-012`, `FR-M1-017` | `M1-I03`, `M1-I10`–`M1-I12`, `M1-I14`–`M1-I18`, `M1-I24` |
| `CONF-M1-026`–`029`, `031` | `INT-M1-006` | `FR-M1-006`–`FR-M1-009` | `M1-I11`, `M1-I17`, `M1-I18` |
| `CONF-M1-030` | all external contracts | `FR-M1-002`, `FR-M1-006`, `FR-M1-011`, `FR-M1-017` | `M1-I02`, `M1-I03`, `M1-I24` |
| `CONF-M1-032` | `INT-M1-004` | `FR-M1-006`, `FR-M1-007`, `FR-M1-017` | `M1-I01`, `M1-I03`, `M1-I11` |

## Harness rules

- Create only broker-owned, uniquely named fixtures; never point conformance tests at a
  user's Workspace or arbitrary provider resources.
- Inject transport loss and process restart at intent, dispatch, observation, and record
  boundaries to exercise ambiguity rather than only happy paths.
- Verify negative authority by attempting forbidden paths, endpoints, origins, profile
  fields, and credentials from the least-trusted side.
- Compare normalized codes and structured fields, never provider error strings.
- Retain sanitized evidence in the control-plane trust zone and treat raw command output
  as potentially secret-bearing.
