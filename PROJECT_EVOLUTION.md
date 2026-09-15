# Project Evolution — Windows

<!-- evolution:reviewed=2026-09-15; timestamp=2026-09-15T00:00:00+02:00; tag=#Windows; owner=antonysc -->

## Start Here

| Field | Current truth |
| --- | --- |
| Goal | Normalize Azure and Microsoft Store capabilities behind isolated, composable and multi-account connectors. |
| State | `active` |
| Current release | `REL-001` — repository and two-pod connector foundation |
| Delivered | Architecture, API/action matrices, profiles, permissions, costs, monitoring, secret backends, environment farm, Go read-only probes and CI contracts |
| Next step | Bind least-privilege protected identities and run both discovery profiles |
| Live status | `WAITING_CONFIGURATION`; no Microsoft credential is stored in Git |
| Production | `WAITING_APPROVAL`; deployment and release profiles are disabled |

## Architecture

`windows` is a composition boundary, not a shared identity. The `azure` and
`microsoft-store` sub-pods own independent accounts, scopes, catalogs and
approval gates. `contracts/` and normalized status semantics are shared.

The runner farm separates Linux control-plane and Azure workloads from Windows
packaging/signing workloads. A protected GitLab Runner is the primary target;
GitHub Actions validates the repository and can execute manual read-only probes.

## Roadmap

| ID | Outcome | Status | Evidence / gate |
| --- | --- | --- | --- |
| `WIN-001` | Establish the shared contract and two isolated sub-pods | `verified` | manifest, account boundaries and profiles |
| `WIN-002` | Inventory normalized Azure deployment, operations, monitoring and cost surfaces | `verified` | human and JSON matrices |
| `WIN-003` | Inventory Store packaging, submission, flighting and release surfaces | `verified` | human and JSON matrices |
| `WIN-004` | Verify Azure read-only connection using workload identity or service principal | `waiting_configuration` | subscription list succeeds without secret disclosure |
| `WIN-005` | Verify Store read-only connection through Entra and Partner Center | `waiting_configuration` | product draft metadata query succeeds |
| `WIN-006` | Enable non-production Azure deployment | `planned` | IaC plan, policy, budget, idempotency and approval evidence |
| `WIN-007` | Enable Store package delivery and flighting | `planned` | signed package, WACK result, identity and rollout evidence |
| `WIN-008` | Enable production Azure and Store release | `waiting_approval` | two-person approval, immutable artifact and rollback plan |
| `WIN-009` | Replace long-lived runner secrets with federated or brokered credentials | `planned` | OIDC federation and audited secret leases |

## Decisions

### `D-001` — Separate Azure and Store identities

Azure resource administration and Partner Center publication have different
blast radii, account owners and permission models. They remain independently
selectable even if one Entra tenant eventually owns both.

### `D-002` — Multi-account by configuration, not duplicated code

Every account is a named record with a pod, environment, tenant, scope and
credential references. Profiles select an account; adapters never hard-code it.

### `D-003` — Headless does not mean unauthenticated

Connections are non-interactive and containerized, but always authenticated.
Azure prefers workload identity federation or managed identity. The Store POC
uses a Partner Center-linked Entra application until federation is supported
end to end.

### `D-004` — Discovery before mutation

Only bounded read probes are enabled. RBAC, deployments, pricing, submissions,
flight creation and production release stay disabled until their gates pass.

### `D-005` — Azure is mapped under Windows

`Azure` is the `azure` sub-pod of `antonysc/Windows`, not a standalone
repository. Repository-creation agents must consult the durable application map,
report this existing relationship, and refuse duplicate top-level creation
unless the owner explicitly overrides the mapping.

## Release `REL-001`

Rollout: validate contracts and container → bind protected variables → run
read-only discovery → record evidence → enable monitoring → separately approve
non-production delivery. Rollback: disable schedules, revoke credentials and
remove runner variables. Discovery does not modify Azure or Store data.

## Timeline

| Timestamp | Tag | Event | Result | Next |
| --- | --- | --- | --- | --- |
| `2026-09-12T08:05:25+02:00` | `#Windows` | Repository initialized using the Apple provider methodology | Two isolated sub-pods, shared contract and rollout controls prepared | Bind protected identities and verify discovery |
| `2026-09-15` | `#Windows` | Owner reconfirmed the Azure → Windows mapping and required cross-agent memory | Mapping made explicit in AGENTS.md, CLAUDE.md and shared application cartography | Consult the map before every repository mutation |
