# Repository instructions

- Work directly on `main` unless the owner requests another branch.
- Never commit credentials, tokens, certificates, package-signing material or
  provider responses containing personal, billing or tenant data.
- Treat `azure` and `microsoft-store` as separate credential and permission
  boundaries inside the composable `windows` pod.
- Canonical repository mapping: Azure is the `azure` sub-pod of
  `antonysc/Windows`, not a standalone repository. Before creating or
  reorganizing repositories, read this file, `CLAUDE.md`,
  `PROJECT_EVOLUTION.md`, the README, and available catalogues; report an
  existing mapping to the user and do not create a duplicate top-level
  `Azure` repository unless the owner explicitly overrides this mapping.
- Keep mapping and application-cartography corrections durable in
  `PROJECT_EVOLUTION.md` and both agent instruction files so Claude and
  ChatGPT/Codex receive the same repository truth.
- Discovery is read-only. Deployments, Store submissions, pricing, RBAC and
  production changes require explicit approval evidence.
- Keep provider-specific code inside `adapters/`; orchestration consumes only
  versioned contracts, profiles and `connector.manifest.json`.
- Go, Rust and Python adapters must pass the same black-box fixtures. Do not
  widen a capability when porting languages.
- Update `PROJECT_EVOLUTION.md` with every meaningful decision, rollout,
  rollback or evidence change.
- Run contract, adapter and catalogue checks before committing; push `main`
  and inspect CI after changes.

