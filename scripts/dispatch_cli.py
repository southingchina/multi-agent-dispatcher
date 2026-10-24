#!/usr/bin/env python3
"""Dispatch one configured CLI node and write a normalized result."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import time
import uuid
from workbuddy_cli_activity import run_workbuddy
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = SKILL_ROOT / "assets" / "agent-registry.json"


def repair_mojibake(value: str) -> str:
    """Preserve UTF-8 subprocess output; never guess a second encoding."""
    return value


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def expand(
    parts: list[str], prompt: str, timeout: int, working_dir: Path | None = None
) -> list[str]:
    resolved_working_dir = working_dir or Path.cwd()
    return [
        part.replace("{skill_root}", str(SKILL_ROOT))
        .replace("{prompt}", prompt)
        .replace("{prompt_shell}", shell_quote(prompt))
        .replace("{timeout}", str(timeout))
        .replace("{working_dir}", str(resolved_working_dir))
        for part in parts
    ]


def select_model(agent: dict, requested_model: str | None) -> str | None:
    model = requested_model or agent.get("model")
    allowed_models = agent.get("allowed_models", [])
    if model and allowed_models and model not in allowed_models:
        raise ValueError(f"Model is not allowed for {agent['id']}: {model}")
    return model


def build_command(
    agent: dict,
    prompt: str,
    timeout: int,
    model: str | None,
    working_dir: Path,
    allow_working_dir: bool,
    allow_writes: bool,
) -> list[str]:
    command = expand(
        agent["command"] + agent.get("args", []), prompt, timeout, working_dir
    )
    if not allow_working_dir:
        restricted: list[str] = []
        skip_next = False
        for part in command:
            if skip_next:
                skip_next = False
                continue
            if part == "--add-dir":
                skip_next = True
                continue
            restricted.append(part)
        command = restricted
    if agent["id"] == "workbuddy-cli":
        if not allow_working_dir:
            command.extend(["--tools", ""])
        elif not allow_writes:
            command.extend(["--permission-mode", "plan"])
    elif agent["id"] == "antigravity-cli" and not allow_writes:
        command.extend(["--mode", "plan"])
    if agent["id"] == "antigravity-cli":
        for prompt_flag in ("-p", "--print", "--prompt"):
            if prompt_flag in command:
                index = command.index(prompt_flag)
                del command[index : index + 2]
                break
        command.extend(
            ["--input-format", "stream-json", "--output-format", "stream-json"]
        )
    if not model:
        return command
    if agent["id"] != "antigravity-cli":
        raise ValueError(f"Model selection is not supported for {agent['id']}")
    return [command[0], "--model", model, *command[1:]]


def parse_codebuddy_stdout(stdout: str) -> str:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return ""
    items = payload if isinstance(payload, list) else [payload]
    for item in reversed(items):
        if isinstance(item, dict) and item.get("type") == "result":
            result = item.get("result")
            if isinstance(result, str):
                return repair_mojibake(result.strip())
    return ""


def valid_final_response(response: str) -> bool:
    stripped = response.strip()
    if not stripped:
        return False
    tool_only_markers = ("<tool_calls:", "<tool_call:")
    return not stripped.startswith(tool_only_markers)


def parse_antigravity_stdout(stdout: str) -> tuple[str, str | None]:
    response = ""
    session_id = None
    for line in stdout.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("event") == "init" and isinstance(item.get("conversation_id"), str):
            session_id = item["conversation_id"]
        result = item.get("result")
        if item.get("event") == "result" and isinstance(result, dict):
            if isinstance(result.get("conversation_id"), str):
                session_id = result["conversation_id"]
            if isinstance(result.get("response"), str):
                response = result["response"]
    return repair_mojibake(response.strip()), session_id


def parse_antigravity(
    started: float, session_id: str | None
) -> tuple[str, Path | None]:
    root = Path.home() / ".gemini" / "antigravity-cli"
    if not isinstance(session_id, str) or not session_id:
        return "", None
    log = root / "brain" / session_id / ".system_generated" / "logs" / "transcript_full.jsonl"
    if not log.is_file() or log.stat().st_mtime < started - 5:
        return "", None
    if not log:
        return "", None
    response = ""
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "PLANNER_RESPONSE" and isinstance(item.get("content"), str):
            response = item["content"]
    return repair_mojibake(response.strip()), log


def cleanup_antigravity_session(log: Path | None, started: float) -> list[str]:
    """Remove only the Antigravity CLI session created for this dispatch."""
    if not log:
        return []
    session_dir = log.parents[2]
    session_id = session_dir.name
    brain_root = Path.home() / ".gemini" / "antigravity-cli" / "brain"
    if session_dir.parent != brain_root or not session_id:
        return []

    removed: list[str] = []
    session_existed = session_dir.exists()
    shutil.rmtree(session_dir, ignore_errors=True)
    if session_existed and not session_dir.exists():
        removed.append(str(session_dir))

    conversations = Path.home() / ".gemini" / "antigravity-cli" / "conversations"
    for suffix in (".db", ".db-wal", ".db-shm"):
        candidate = conversations / f"{session_id}{suffix}"
        existed = candidate.exists()
        try:
            candidate.unlink(missing_ok=True)
        except OSError:
            continue
        if existed and not candidate.exists():
            removed.append(str(candidate))

    log_root = Path.home() / ".gemini" / "antigravity-cli" / "log"
    recent_logs = (
        sorted(
            (p for p in log_root.glob("cli-*.log") if p.stat().st_mtime >= started - 5),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if log_root.exists()
        else []
    )
    for recent_log in recent_logs:
        try:
            if session_id in recent_log.read_text(encoding="utf-8", errors="replace"):
                recent_log.unlink(missing_ok=True)
                removed.append(str(recent_log))
                break
        except OSError:
            continue

    summaries = (
        Path.home()
        / ".gemini"
        / "antigravity-cli"
        / "conversation_summaries.db"
    )
    try:
        with sqlite3.connect(summaries) as connection:
            deleted = connection.execute(
                "DELETE FROM conversation_summaries WHERE conversation_id = ?",
                (session_id,),
            ).rowcount
            connection.commit()
        if deleted:
            removed.append(f"{summaries}#{session_id}")
    except sqlite3.Error:
        pass
    return removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--job-dir", type=Path, required=True)
    parser.add_argument("--working-dir", type=Path)
    parser.add_argument(
        "--allow-working-dir",
        action="store_true",
        help="Allow the selected node to read the explicitly supplied working directory",
    )
    parser.add_argument(
        "--allow-writes",
        action="store_true",
        help="Allow writes in the authorized working directory; requires --allow-working-dir",
    )
    parser.add_argument("--job-id")
    parser.add_argument("--task-title", help="Short display title for WB CLI activity cards")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--model")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    agent = next((a for a in registry["agents"] if a["id"] == args.agent), None)
    if not agent:
        raise SystemExit(f"Unknown agent: {args.agent}")
    if not agent["enabled"]:
        raise SystemExit(f"Agent is disabled: {args.agent}")
    if agent["surface"] != "cli":
        raise SystemExit(f"dispatch_cli.py only accepts CLI nodes: {args.agent}")
    if args.allow_writes and not args.allow_working_dir:
        raise SystemExit("--allow-writes requires --allow-working-dir")

    timeout = args.timeout or int(agent.get("timeout_seconds", 300))
    working_dir = args.working_dir.resolve() if args.working_dir else Path.cwd().resolve()
    if not working_dir.is_dir():
        raise SystemExit(f"Working directory does not exist: {working_dir}")
    job_id = args.job_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:6]
    args.job_dir.mkdir(parents=True, exist_ok=True)
    try:
        selected_model = select_model(agent, args.model)
        command = build_command(
            agent,
            args.prompt,
            timeout,
            selected_model,
            working_dir,
            args.allow_working_dir,
            args.allow_writes,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    started_wall = time.time()
    started = time.monotonic()
    status = "failed"
    exit_code = None
    stdout = ""
    stderr = ""
    artifact = None
    launched = False
    errors: list[str] = []

    process_cwd = args.job_dir.resolve()
    process_env = os.environ.copy()
    if agent["id"] == "antigravity-cli" and agent.get("proxy_url"):
        process_env["HTTP_PROXY"] = agent["proxy_url"]
        process_env["HTTPS_PROXY"] = agent["proxy_url"]
    stdin_payload = None
    if agent["id"] == "antigravity-cli":
        stdin_payload = json.dumps(
            {
                "event": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": args.prompt}],
                },
            },
            ensure_ascii=False,
        ) + "\n"
    try:
        if agent["id"] == "workbuddy-cli":
            completed = run_workbuddy(
                command, timeout=timeout, cwd=process_cwd, env=process_env,
                job_id=job_id, title=args.task_title or args.job_id or args.job_dir.parent.name,
                model=selected_model or agent.get("reported_model"),
            )
        else:
            completed = subprocess.run(
                command,
                input=stdin_payload,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
                cwd=process_cwd,
                env=process_env,
            )
        launched = True
        exit_code = completed.returncode
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
    except subprocess.TimeoutExpired as exc:
        status = "timed_out"
        stdout = (exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else ""
        errors.append(f"Timed out after {timeout} seconds")
    except OSError as exc:
        errors.append(str(exc))

    parser_name = agent.get("response_parser", "plain-text")
    response = stdout
    if parser_name == "codebuddy-log":
        response = parse_codebuddy_stdout(stdout)
    elif parser_name == "antigravity-log":
        stream_response, session_id = parse_antigravity_stdout(stdout)
        parsed_response, artifact = (
            parse_antigravity(started_wall, session_id)
            if launched or session_id
            else ("", None)
        )
        response = stream_response or parsed_response

    if status != "timed_out":
        diagnostic = "\n".join(part for part in (stdout, stderr) if part).casefold()
        if agent["id"] == "workbuddy-cli" and (
            "authentication required" in diagnostic
            or "please use /login command" in diagnostic
        ):
            status = "blocked_auth"
            errors.append(stderr or stdout)
        elif exit_code == 0 and valid_final_response(response):
            status = "completed"
        elif exit_code == 0:
            status = "completed_no_response"
            if response:
                errors.append("Response contained tool-call markup but no final answer")
        else:
            status = "failed"
            if stderr:
                errors.append(stderr)

    formal_artifact = None
    if parser_name == "antigravity-log" and artifact:
        formal_artifact = args.job_dir / "antigravity-transcript.jsonl"
        try:
            shutil.copy2(artifact, formal_artifact)
        except OSError as exc:
            errors.append(f"Could not preserve Antigravity transcript: {exc}")
            formal_artifact = None

    result = {
        "schema_version": 1,
        "job_id": job_id,
        "agent_id": agent["id"],
        "family": agent["family"],
        "surface": "cli",
        "model": selected_model or agent.get("reported_model"),
        "working_directory": str(working_dir) if args.allow_working_dir else None,
        "directory_access": (
            "workspace_write"
            if args.allow_writes
            else "read_only"
            if args.allow_working_dir
            else "prompt_only"
        ),
        "process_directory": str(process_cwd),
        "status": status,
        "response": repair_mojibake(response),
        "raw_output": repair_mojibake(
            stdout + ("\n[stderr]\n" + stderr if stderr else "")
        ),
        "artifacts": [str(formal_artifact)] if formal_artifact else [],
        "ephemeral_cleanup": [],
        "duration_seconds": round(time.monotonic() - started, 3),
        "exit_code": exit_code,
        "acceptance": "pending",
        "errors": errors,
    }
    output = args.job_dir / "result.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if parser_name == "antigravity-log" and artifact and formal_artifact:
        result["ephemeral_cleanup"] = cleanup_antigravity_session(
            artifact, started_wall
        )
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
