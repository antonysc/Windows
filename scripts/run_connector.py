#!/usr/bin/env python3
"""Run a Windows connector profile without exposing credential values."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def emit(status: str, profile: str, pod: str, detail: str, exit_code: int) -> int:
    print(json.dumps({
        "schema_version": 1,
        "provider": "windows",
        "pod": pod,
        "profile": profile,
        "status": status,
        "detail": detail,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }, separators=(",", ":")))
    return exit_code


def credential_environment(account: dict[str, Any], required: list[str]) -> tuple[dict[str, str], list[str]]:
    environment = os.environ.copy()
    missing = []
    for name in required:
        reference = account["credentials"].get(name, "")
        if not reference.startswith("env://"):
            missing.append(name)
            continue
        variable = reference.removeprefix("env://")
        if not os.environ.get(variable):
            missing.append(variable)
    return environment, missing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--approval-ref")
    args = parser.parse_args()

    profiles = (ROOT / "profiles").resolve()
    profile_path = (profiles / f"{args.profile}.json").resolve()
    if profile_path.parent != profiles or not profile_path.is_file():
        return emit("FAILED", args.profile, "unknown", "unknown profile", 1)
    profile = load(profile_path)
    pod = profile["pod"]
    if args.describe:
        print(json.dumps(profile, indent=2))
        return 0
    if not profile.get("enabled", False):
        return emit("WAITING_CONFIGURATION", args.profile, pod, "profile is disabled", 2)
    if profile.get("risk") == "approval_required" and not args.approval_ref:
        return emit("WAITING_APPROVAL", args.profile, pod, "approval reference is required", 3)

    manifest = load(ROOT / "connector.manifest.json")
    accounts = load(ROOT / "config" / "accounts.json")["accounts"]
    account = accounts[profile["account"]]
    if account["pod"] != pod:
        return emit("FAILED", args.profile, pod, "profile/account pod mismatch", 1)
    environment, missing = credential_environment(account, profile.get("required_credentials", []))
    if missing:
        return emit("WAITING_CONFIGURATION", args.profile, pod, "missing protected credentials: " + ",".join(missing), 2)

    runtime = profile.get("runtime", manifest["default_runtime"])
    implementation = manifest["implementations"].get(runtime)
    if not implementation or implementation["status"] == "planned":
        return emit("WAITING_CONFIGURATION", args.profile, pod, "selected adapter is not implemented", 2)
    for capability in profile["commands"]:
        command = implementation["commands"].get(capability)
        if not command:
            return emit("WAITING_CONFIGURATION", args.profile, pod, f"no adapter for {capability}", 2)
        completed = subprocess.run(command, cwd=ROOT, env=environment, check=False)
        if completed.returncode != 0:
            return emit("DEGRADED", args.profile, pod, f"adapter failed for {capability}", 1)
    return emit("SUCCEEDED", args.profile, pod, "all profile commands completed", 0)


if __name__ == "__main__":
    sys.exit(main())

