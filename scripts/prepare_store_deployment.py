#!/usr/bin/env python3
"""Validate and normalize a Microsoft Store deployment plan without publishing it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
ENV_REFERENCE = re.compile(r"^env://[A-Z][A-Z0-9_]*$")
MARKET = re.compile(r"^[A-Z]{2}$")
PACKAGE_TYPES = {"exe", "msi", "msix", "pwa"}
ARCHITECTURES = {"x86", "x64", "arm64", "neutral"}
PUBLISH_MODES = {"hold", "scheduled", "automatic"}
ENVIRONMENTS = {"development", "test", "staging", "production"}


class InvalidPlan(ValueError):
    """Raised when a deployment plan violates the bounded Store contract."""


def require_string(document: dict[str, Any], name: str) -> str:
    value = document.get(name)
    if not isinstance(value, str) or not value.strip():
        raise InvalidPlan(f"{name} must be a non-empty string")
    return value.strip()


def require_string_list(document: dict[str, Any], name: str) -> list[str]:
    value = document.get(name)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise InvalidPlan(f"{name} must be a non-empty list of strings")
    return [item.strip() for item in value]


def load_plan(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise InvalidPlan(f"unable to read deployment plan: {error}") from error
    if not isinstance(document, dict):
        raise InvalidPlan("deployment plan must be a JSON object")
    return document


def normalize(document: dict[str, Any], approval_ref: str | None) -> dict[str, Any]:
    if document.get("schema_version") != 1:
        raise InvalidPlan("schema_version must be 1")
    if document.get("pod") != "microsoft-store":
        raise InvalidPlan("pod must be microsoft-store")

    account = require_string(document, "account")
    environment = require_string(document, "environment")
    if environment not in ENVIRONMENTS:
        raise InvalidPlan(f"environment must be one of {sorted(ENVIRONMENTS)}")
    digest = require_string(document, "artifactDigest")
    if not SHA256.fullmatch(digest):
        raise InvalidPlan("artifactDigest must be a lowercase sha256 digest")
    idempotency_key = require_string(document, "idempotencyKey")

    store = document.get("microsoftStore")
    if not isinstance(store, dict):
        raise InvalidPlan("microsoftStore must be an object")
    product_id = require_string(store, "productId")
    if not ENV_REFERENCE.fullmatch(product_id):
        raise InvalidPlan("productId must be an env:// reference, never a live identifier in Git")
    package_type = require_string(store, "packageType")
    if package_type not in PACKAGE_TYPES:
        raise InvalidPlan(f"packageType must be one of {sorted(PACKAGE_TYPES)}")
    publish_mode = require_string(store, "publishMode")
    if publish_mode not in PUBLISH_MODES:
        raise InvalidPlan(f"publishMode must be one of {sorted(PUBLISH_MODES)}")

    package_path = store.get("packagePath")
    installer_url = store.get("installerUrl")
    if package_type == "msix" and not isinstance(package_path, str):
        raise InvalidPlan("packagePath is required for packageType msix")
    if package_type in {"exe", "msi", "pwa"} and not isinstance(installer_url, str):
        raise InvalidPlan(f"installerUrl is required for packageType {package_type}")
    if isinstance(package_path, str):
        candidate = Path(package_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise InvalidPlan("packagePath must be repository-relative")
    if isinstance(installer_url, str) and not installer_url.startswith("https://"):
        raise InvalidPlan("installerUrl must use HTTPS")

    approval = (approval_ref or document.get("approvalRef") or "").strip()
    approval_required = environment == "production" or publish_mode != "hold"
    status = "WAITING_APPROVAL" if approval_required and not approval else "READY"

    architectures = require_string_list(store, "architectures")
    if any(item not in ARCHITECTURES for item in architectures):
        raise InvalidPlan(f"architectures must use values from {sorted(ARCHITECTURES)}")
    markets = require_string_list(store, "markets")
    if any(not MARKET.fullmatch(item) for item in markets):
        raise InvalidPlan("markets must contain uppercase ISO two-letter codes")

    normalized_store: dict[str, Any] = {
        "productIdReference": product_id,
        "packageType": package_type,
        "publishMode": publish_mode,
        "architectures": architectures,
        "languages": require_string_list(store, "languages"),
        "markets": markets,
    }
    if isinstance(package_path, str):
        normalized_store["packagePath"] = package_path
    if isinstance(installer_url, str):
        normalized_store["installerUrl"] = installer_url
    if isinstance(store.get("flightId"), str) and store["flightId"].strip():
        normalized_store["flightId"] = store["flightId"].strip()

    return {
        "schema_version": 1,
        "provider": "windows",
        "pod": "microsoft-store",
        "account": account,
        "environment": environment,
        "artifactDigest": digest,
        "idempotencyKey": idempotency_key,
        "approvalRef": approval or None,
        "status": status,
        "action": "plan_only",
        "microsoftStore": normalized_store,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--approval-ref")
    args = parser.parse_args()

    path = (args.config if args.config.is_absolute() else ROOT / args.config).resolve()
    if path != ROOT and ROOT not in path.parents:
        print(json.dumps({"status": "FAILED", "detail": "deployment plan must be inside the repository"}, separators=(",", ":")))
        return 1
    try:
        result = normalize(load_plan(path), args.approval_ref)
    except InvalidPlan as error:
        print(json.dumps({"status": "FAILED", "detail": str(error)}, separators=(",", ":")))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "READY" else 3


if __name__ == "__main__":
    sys.exit(main())
