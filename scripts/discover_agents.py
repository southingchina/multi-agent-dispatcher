#!/usr/bin/env python3
"""Report configured agent readiness without sending prompts."""

from __future__ import annotations

import argparse
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = SKILL_ROOT / "assets" / "agent-registry.json"


def command_exists(command: list[str]) -> bool:
    if not command:
        return False
    executable = command[0]
    if Path(executable).is_absolute():
        if not Path(executable).exists():
            return False
    elif shutil.which(executable) is None:
        return False
    return all(Path(part).exists() for part in command[1:] if Path(part).is_absolute())


def expand_skill_root(parts: list[str]) -> list[str]:
    return [part.replace("{skill_root}", str(SKILL_ROOT)) for part in parts]


def cdp_ready(endpoint: str) -> bool:
    try:
        with urllib.request.urlopen(f"{endpoint.rstrip('/')}/json/list", timeout=1) as response:
            targets = json.load(response)
    except (OSError, urllib.error.URLError, ValueError):
        return False
    return any(
        item.get("type") == "page"
        and str(item.get("url", "")).startswith("doubao://doubao-chat/chat")
        for item in targets
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    results = []
    for agent in registry["agents"]:
        surface = agent["surface"]
        if surface == "web":
            available = bool(agent.get("url"))
            readiness = "browser_login_unverified" if available else "missing_url"
        elif agent.get("adapter") == "doubao-cdp":
            available = cdp_ready(agent.get("cdp_endpoint", ""))
            readiness = "ready" if available else "cdp_restart_or_launch_required"
        elif agent.get("adapter") == "workbuddy-ipc":
            command_available = command_exists(expand_skill_root(agent.get("command", [])))
            endpoint_file = agent.get("ipc_endpoint_file")
            available = command_available and bool(endpoint_file) and Path(endpoint_file).is_file()
            readiness = "ipc_probe_required" if available else "missing_command_or_ipc_endpoint"
        elif surface == "desktop":
            available = None
            readiness = "ui_check_required"
        else:
            available = command_exists(expand_skill_root(agent.get("command", [])))
            readiness = "ready" if available else "missing_command"
        results.append(
            {
                "id": agent["id"],
                "family": agent["family"],
                "surface": surface,
                "enabled": agent["enabled"],
                "available": available,
                "readiness": readiness,
            }
        )

    report = {"schema_version": 1, "agents": results}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
