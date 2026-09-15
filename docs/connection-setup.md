# Connection setup

The repository contains no live credential. It provides repeatable shells in
which protected values can be bound for one or more accounts.

## Azure

Preferred production flow:

```text
protected GitLab/GitHub job
  -> OIDC token
  -> Entra federated credential
  -> short-lived Azure access token
  -> Azure Resource Manager
```

Bootstrap:

1. Select the tenant and subscription.
2. Create a dedicated app registration or user-assigned managed identity.
3. Add a federated identity credential bound to the exact repository, protected
   branch/environment and token audience.
4. Assign `Reader` at the smallest scope needed for discovery. Add Monitoring
   and Cost readers separately only for monitoring.
5. Store these non-secret identifiers as protected configuration:
   `AZURE_PROD_TENANT_ID`, `AZURE_PROD_CLIENT_ID`,
   `AZURE_PROD_SUBSCRIPTION_ID`.
6. Let the runner expose a job-scoped federated token file as
   `AZURE_PROD_FEDERATED_TOKEN_FILE`.

The initial local POC uses the `azure-dev` client-secret fallback because it can
be tested without coupling the contract to one CI issuer. Bind:

| Variable | Meaning | Sensitivity |
| --- | --- | --- |
| `AZURE_DEV_TENANT_ID` | Entra tenant | protected configuration |
| `AZURE_DEV_CLIENT_ID` | dedicated app registration | protected configuration |
| `AZURE_DEV_CLIENT_SECRET` | temporary client credential | secret |
| `AZURE_DEV_SUBSCRIPTION_ID` | bounded discovery target | protected configuration |

Run `python scripts/run_connector.py --profile azure-discovery`. The probe
obtains a token for `https://management.azure.com/.default`, reads exactly one
subscription resource and discards the response body.

## Microsoft Store

Bootstrap is partly manual by design:

1. Complete Partner Center legal, contact, tax and payout records as required.
2. Reserve the app name and create the first product in Partner Center.
3. Complete the first submission prerequisites, including age rating; the API
   cannot replace every first-time portal action.
4. Register a dedicated Entra application and associate it with the Partner
   Center account.
5. Prefer a certificate kept in a signing/secret service. The initial POC also
   supports a client secret; rotate it after validation.
6. Bind the following protected values:

| Variable | Meaning | Sensitivity |
| --- | --- | --- |
| `MS_STORE_PROD_TENANT_ID` | Entra tenant | protected configuration |
| `MS_STORE_PROD_CLIENT_ID` | Partner Center-linked application | protected configuration |
| `MS_STORE_PROD_CLIENT_SECRET` | client credential | secret |
| `MS_STORE_PROD_SELLER_ID` | Partner Center seller ID | protected configuration |
| `MS_STORE_PROD_PRODUCT_ID` | bounded test product | protected configuration |

Run `python scripts/run_connector.py --profile store-discovery`. The probe
requests the Store scope, sends `X-Seller-Account-Id`, reads only the English
draft metadata for the configured product and discards the body.

### Parameterized GitHub deployment entry point

`config/microsoft-store-deployment.example.json` is the non-secret deployment
contract for an app. Copy it for each product and select the package type,
architectures, languages, markets and publication mode. Keep the product ID as
an `env://` reference; never commit a live Partner Center identifier or secret.

Validate a plan without contacting Microsoft:

```text
python scripts/prepare_store_deployment.py \
  --config config/microsoft-store-deployment.example.json
```

The `Microsoft Store connector` GitHub workflow exposes the profile and plan as
manual parameters. `store-discovery` can run the bounded read-only probe after
repository variables and the client-secret secret are configured. Delivery and
release selections remain validation-only until their repository profiles and
approval gates are deliberately enabled.

## Evidence and promotion

Expected states:

```text
missing variables or toolchain -> WAITING_CONFIGURATION
token rejected                 -> DEGRADED / REJECTED_AUTHENTICATION
scope or role rejected         -> DEGRADED / REJECTED_PERMISSION
bounded HTTP 200               -> SUCCEEDED (discovery only)
```

After a successful probe, record the account, scope, role, request/correlation
ID, adapter digest and timestamp—never the token or response payload. Then
enable the corresponding monitoring profile. Delivery remains disabled.

## Rollback

Disable the scheduled job, revoke the federated credential or Store connector
credential, remove protected runner variables and invalidate outstanding
sessions. Discovery has no provider-data recovery step because it performs no
mutation.

