# Azure and Microsoft Store API matrix

`2026-09-12T08:05:25+02:00` — `#Windows`

Machine-readable details, inputs, outputs and monitoring fields are in
`catalog/azure-capabilities.json` and
`catalog/microsoft-store-capabilities.json`.

## Normalized action matrix

| Pod | Domain | Read/discovery | Controlled action | Approval-required action | Interface |
| --- | --- | --- | --- | --- | --- |
| Azure | Identity/scope | tenant, subscription, provider and resource inventory | none | federation/RBAC changes | Entra OAuth2, ARM, Resource Graph |
| Azure | Infrastructure | deployment state and What-If | dev deployment | production apply, cancel, delete | ARM/Bicep, Azure CLI |
| Azure | Compute | App Service, Functions, Container Apps, AKS state | dev artifact/revision deploy | production or cluster topology change | service REST APIs, CLI |
| Azure | Containers | registry/repository/digest read | push signed image | retention purge or trust-policy change | ACR/OCI |
| Azure | Data | resource metadata and health | migrations explicitly scoped | create/delete database, storage or data-plane access | service REST/data APIs |
| Azure | Security | policy/RBAC/Key Vault metadata | alert/remediation workflow | RBAC, policy, vault or network mutation | Authorization, Policy, Key Vault |
| Azure | Observability | metrics, logs, health, activity | alert-rule changes | diagnostic removal or retention reduction | Azure Monitor, Log Analytics |
| Azure | Cost | actual, forecast and price discovery | notifications | budget/commitment changes | Cost Management, Consumption, Retail Prices |
| Store | Account/app | product and identity read | project initialization | initial account/legal/product bootstrap | Partner Center UI + CLI/API |
| Store | Package | package metadata and validation status | build, sign request, WACK, upload draft | replace production artifact after approval freeze | msstore CLI, WACK, submission API |
| Store | Listing | listing/assets read | draft metadata update | price, market, visibility or audience change | submission metadata API |
| Store | Submission | draft/status/certification read | test draft and flight update | submit, publish, delete | msstore submission commands/API |
| Store | Flights | list/get flights and rollout | create/update test flight | delete flight or production rollout | msstore flights/submission rollout |
| Store | Analytics | acquisition, usage and health read | none | export expansion containing sensitive data | Partner Center analytics APIs |

## Request and command paths

| Capability | HTTP/API path | Representative command | Key inputs | Normalized output |
| --- | --- | --- | --- | --- |
| Azure connection | `GET /subscriptions/{id}?api-version=2022-12-01` | `az account show` | tenant, workload identity, subscription | status, request ID, observed time |
| Azure API discovery | `GET /subscriptions/{id}/providers` | `az provider list` | subscription, pinned version | namespaces, types, versions, locations |
| Azure inventory | `POST /providers/Microsoft.ResourceGraph/resources` | `az graph query` | scopes, KQL query | resources, facets, continuation |
| Azure preview | `POST .../deployments/{name}/whatIf` | `az deployment group what-if` | immutable template, parameters, scope | changes, diagnostics, policy failures |
| Azure apply | `PUT .../deployments/{name}` | `az deployment group create` | artifact digest, parameters, approval | operation ID, state, outputs, cost context |
| Azure monitoring | `Microsoft.Insights` and `OperationalInsights` APIs | `az monitor ...` | resource/query/timespan | metrics/log rows/health with freshness |
| Azure cost | `POST .../Microsoft.CostManagement/query` | `az rest` | billing scope, timeframe, dataset | rows, currency, actual/forecast |
| Store token | Entra `/oauth2/v2.0/token` | CLI internal auth | tenant, client credential, Store scope | short-lived access token (never logged) |
| Store draft read | `GET /submission/v1/product/{id}/metadata` | `msstore submission get` | product, languages, seller | module/draft status |
| Store metadata | `PUT .../metadata/{module}` | `msstore submission updateMetadata` | current draft JSON, locales | validation and module status |
| Store package | Store package API/CLI abstraction | `msstore submission update` | immutable package/URL and digest | upload/package state |
| Store publish | `POST /submission/v1/product/{id}/submit` | `msstore submission publish` | ready modules, approval, schedule | correlation ID, certification state |
| Store status | submission status endpoint | `msstore submission status` / `poll` | product/submission | state, errors, retry interval |
| Store flights | flight/submission resources | `msstore flights ...` | app, flight, audience, package | flight/submission/rollout state |

## Permissions matrix

| Profile | Azure minimum starting point | Store minimum starting point | Forbidden routine identity |
| --- | --- | --- | --- |
| Discovery | `Reader` on a bounded scope | linked app with product read | Global Admin, Owner, account owner |
| Monitoring | Reader + Monitoring Reader + Cost Management Reader as needed | submission/certification/analytics read | publishing identity with broad account access |
| Delivery dev | custom resource-group role and separate data-plane grants | dedicated test product/flight write | shared production identity |
| Production | custom exact actions at approved scope, just-in-time elevation | exact product submission/release access | permanent tenant-wide administrator |

## Monitoring matrix

| Layer | Required signals | Alert examples |
| --- | --- | --- |
| Common transport | latency, HTTP status, request/correlation ID, retry-after | auth spike, permission drift, throttling, provider 5xx |
| Azure deployment | What-If delta, deployment operations, policy, Activity Log | unexpected delete, denied policy, stuck deployment |
| Azure runtime | resource health, metrics, logs, revision/slot state | failed revision, availability drop, error-rate SLO |
| Azure cost | actual, forecast, tags, budget threshold | untagged spend, forecast breach, anomalous daily delta |
| Store package | digest, signature, WACK, upload | digest mismatch, expired signing identity, failed validation |
| Store release | draft, certification, flight, rollout, publication | certification failure, stalled state, unintended audience |
| Credential | age, expiry, issuer/subject binding, last use | expired secret, unexpected subject, use outside protected runner |

## Cost matrix

| Surface | API price | What is actually billed | Guardrail |
| --- | --- | --- | --- |
| Azure management APIs | generally no separate request price | provisioned services, storage, execution, logs, network, support | resolve region/SKU price; query Cost Management; enforce budgets |
| Azure monitoring | management read often no separate price | log ingestion, retention, queries, alerts and export | daily cap, sampling, retention policy |
| Microsoft Store API/CLI | no separate request price published | registration/commerce terms, signing infrastructure, EXE/MSI hosting | record current agreement; approval on pricing/markets |
| Runner farm | not a provider API cost | VM/container minutes, cache, artifacts, egress, signing/HSM | ephemeral runners, concurrency caps, artifact retention |

## Explicit non-actions

- No portal password, MFA secret, access token, client secret, certificate or
  signing key is stored in Git, logs, artifacts or command arguments.
- No production deployment, RBAC/policy mutation, Store submission, pricing,
  availability, rollout, deletion or purge occurs during discovery.
- No API preview version is adopted automatically.
- No Azure price is hard-coded as universal; region, SKU, agreement, currency
  and date are resolved at decision time.
- No Store app is created solely through the API: account/legal setup, name
  reservation and first-product prerequisites remain explicit bootstrap gates.

