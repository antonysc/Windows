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



<!-- MAI-ROUTER-V1:BEGIN -->
# Agent Bootstrap — MAI Router V1

This repository participates in the centralized Portfolio / Workflow
orchestration. The canonical routing contract is
`antonysc/Portfolio@main:mai/v1/MAI_CORE.md`; its machine contracts and
registries live beside it in `mai/v1/`.

## Required behavior

- Use MAI Router V1 as the default routing and execution model.
- Determine the active project, repository, and sub-scope before acting.
- Stay strictly inside that scope and activate only the minimum useful domains
  and skills; normally select two to five domains.
- Do not expand into unrelated general knowledge, literary work, or unchecked
  speculation unless the request explicitly requires it.
- Never invent missing project facts. Mark assumptions and uncertainty.
- If a real dependency appears during execution, perform one minimal routing
  expansion and record why it was necessary.
- Prefer concrete outputs: specifications, plans, code, tests, workflows,
  project updates, and validation evidence.
- Follow the repository's local safety, validation, update, and commit rules.
  A local rule may tighten the central contract, but must not silently weaken it.

## Routing result

For each task, determine the routing decision, active scope, active domains,
excluded domains, execution plan, expected artifacts, assumptions, and
out-of-scope items. Render those fields only when they help review or resolve
ambiguity; the routing contract is required even when its presentation remains
implicit.

The governing question is: **what is the smallest useful scope that can move
this task forward correctly?**

Repository routing: `Windows` uses profile `provider_platforms` (revision `1.0.0`); canonical registry: `antonysc/Portfolio@main:mai/v1/PROJECT_SCOPE_REGISTRY.yaml`.
<!-- MAI-ROUTER-V1:END -->
