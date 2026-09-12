# Windows external platform module

`2026-09-12T08:05:25+02:00` — `#Windows`

Isolated and composable integration boundary for Microsoft application and
cloud delivery. The logical `windows` pod contains two independent sub-pods:

- `azure`: cloud resources, services, data, observability and cost controls;
- `microsoft-store`: Windows application packaging, flights, submissions,
  certification and release through Partner Center.

The two sub-pods share one language-neutral orchestration contract, but not
accounts, permissions or credentials. Each supports multiple named accounts
and environments. Go is the initial standard-library-only connectivity POC;
Rust and Python remain replaceable adapters.

Current state: `WAITING_CONFIGURATION`. Read-only discovery is enabled;
mutating delivery and production profiles are disabled and approval-gated.

## Start

1. Read `docs/connection-setup.md` and `docs/api-matrix.md`.
2. Select an Azure or Microsoft Store account in `config/accounts.json`.
3. Put secret values only in protected runner variables or an approved secret
   manager; keep only references in Git.
4. Preview a profile with `python scripts/run_connector.py --profile azure-discovery --describe`.
5. Run a read-only probe after credentials are bound.

The complete platform model is in `docs/architecture.md`. Machine-readable
capabilities live in `catalog/`; identity, permission, cost, monitoring,
runner and secret policy live in `config/`.


