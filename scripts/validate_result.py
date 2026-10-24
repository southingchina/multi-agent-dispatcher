#!/usr/bin/env python3
"""Validate one normalized agent result record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ALLOWED_SURFACES = {"cli", "web", "desktop"}
ALLOWED_STATUSES = {"completed", "completed_no_response", "blocked_auth", "timed_out", "failed"}
ALLOWED_DIRECTORY_ACCESS = {"prompt_only", "read_only", "workspace_write"}
REQUIRED = {
    "schema_version",
    "job_id",
    "agent_id",
    "family",
    "surface",
    "working_directory",
    "directory_access",
    "process_directory",
    "status",
    "response",
    "raw_output",
    "artifacts",
    "ephemeral_cleanup",
    "duration_seconds",
    "acceptance",
    "errors",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.result.read_text(encoding="utf-8"))
    errors = [f"Missing field: {key}" for key in sorted(REQUIRED - payload.keys())]
    if payload.get("surface") not in ALLOWED_SURFACES:
        errors.append(f"Unknown surface: {payload.get('surface')}")
    if payload.get("status") not in ALLOWED_STATUSES:
        errors.append(f"Unknown status: {payload.get('status')}")
    if payload.get("status") == "completed" and not str(payload.get("response", "")).strip():
        errors.append("Completed result has an empty response")
    if not isinstance(payload.get("artifacts"), list):
        errors.append("artifacts must be a list")
    if not isinstance(payload.get("errors"), list):
        errors.append("errors must be a list")
    if payload.get("directory_access") not in ALLOWED_DIRECTORY_ACCESS:
        errors.append(f"Unknown directory_access: {payload.get('directory_access')}")
    if payload.get("directory_access") == "prompt_only" and payload.get("working_directory") is not None:
        errors.append("prompt_only result must have working_directory set to null")
    if not isinstance(payload.get("ephemeral_cleanup"), list):
        errors.append("ephemeral_cleanup must be a list")

    report = {"valid": not errors, "result": str(args.result), "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
