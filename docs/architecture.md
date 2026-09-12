# Windows pod architecture

`2026-09-12T08:05:25+02:00` — `#Windows`

## Composition

```text
Application repositories
        |
        v
normalized command envelope
        |
        v
Windows pod / control plane
        |
        +-- Azure sub-pod ---------- Azure Resource Manager + data planes
        |
        +-- Microsoft Store sub-pod - Entra + Partner Center / Store APIs
        |
        +-- audit, policy, approvals, monitoring
        |
        v
GitLab runner farm / optional GitHub Actions
        |
        +-- ephemeral Linux control runner
        +-- ephemeral Windows packaging runner
        +-- isolated signing service
        +-- secret backend or OIDC broker
```

The parent pod provides discovery, routing, normalized status and audit. Each
sub-pod owns credentials and permission evaluation. A command must always carry
`pod`, `account`, `capability`, `idempotency_key`, `deadline` and, for risky
operations, `approval_context`.

## Account model

Accounts are records, not code forks. Adding another Azure tenant,
subscription, Partner Center seller or Store product adds an account entry and
possibly a profile binding. It does not duplicate adapters.

Recommended hierarchy:

```text
windows
├── azure
│   ├── organization / tenant
│   ├── account / workload identity
│   ├── subscription
│   ├── environment
│   └── resource scope
└── microsoft-store
    ├── organization / tenant
    ├── seller account
    ├── connector identity
    ├── product
    └── flight / submission / environment
```

Do not reuse one powerful Entra application for both pods. Even when the
tenant is shared, use separate app registrations or managed identities,
separate approval paths and separate audit streams.

## Headless connection workflow

1. Bootstrap the human-owned organization, tenant, billing and Partner Center
   records in their portals.
2. Create one least-privilege non-human identity per pod and environment.
3. Prefer federation for Azure; use a certificate or short-lived secret for the
   Store connector where Partner Center requires client credentials.
4. Bind only secret references to the account record.
5. Start an ephemeral container on an allowlisted runner.
6. Resolve identity, mint a short-lived token and run one bounded read request.
7. Emit a redacted normalized result and append audit evidence.
8. Enable monitoring only after discovery succeeds.
9. Enable write profiles independently after their permission, idempotency,
   cost, rollout and rollback gates pass.

"Headless" means non-interactive; it never means unauthenticated.

## Environment farm

| Runner | OS/executor | Responsibilities | Secret lifetime | Isolation |
| --- | --- | --- | --- | --- |
| `linux-control` | ephemeral container | contracts, discovery, Azure plan/apply, API polling | job only | network allowlist, unprivileged |
| `windows-packaging` | ephemeral Windows VM or container where supported | MSIX build, WACK, signing request, Store upload | job only | clean workspace, restricted signing access |
| `signing-service` | isolated service/HSM | sign approved artifacts without exporting private keys | request only | independent audit and policy |
| `monitoring` | scheduled minimal image | read-only state/cost/health probes | short-lived | reader identity only |

For GitLab, register protected runners with scoped tags and disallow untagged
jobs. Production variables and environments must be protected. Serialize by
`account + target` to prevent concurrent deployment or submission conflicts.

## State progression

```text
NOT_CONFIGURED
  -> WAITING_CONFIGURATION
  -> CONNECTED
  -> MONITORED
  -> DELIVERY_READY
  -> TEST_DEPLOYED
  -> PROD_READY
  -> PROD_DEPLOYED
  -> PROD_VERIFIED
```

`WAITING_APPROVAL`, `DEGRADED`, `RETRYABLE`, `REJECTED` and `FAILED` are
side states with evidence. A read-only probe cannot promote a write capability.

## Scaling and resilience

- Partition queues by `pod/account/target`; keep ordering within one target.
- Apply bounded exponential backoff with jitter and honor `Retry-After`.
- Store idempotency keys and provider operation IDs before retrying writes.
- Pin API versions and adapter image digests; alert on schema drift.
- Scale readers separately from deployment and publishing workers.
- Never fail over a financial, RBAC, destructive or release mutation to a
  different account without explicit semantic equivalence and approval.

