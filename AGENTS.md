# Repository instructions

- Work directly on `main` unless the owner requests another branch.
- Never commit credentials, tokens, certificates, package-signing material or
  provider responses containing personal, billing or tenant data.
- Treat `azure` and `microsoft-store` as separate credential and permission
  boundaries inside the composable `windows` pod.
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

