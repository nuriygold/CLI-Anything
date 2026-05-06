"""Execution routing for planned CLI requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cli_anything.litellm.core.execution import ask_model, collect_context, run_shell_command


def _pm2_command(prompt: str) -> str:
    text = prompt.strip().lower()
    if any(keyword in text for keyword in ("list", "show", "status", "processes", "processes", "ls")):
        return "pm2 list"
    if "logs" in text:
        return "pm2 logs"
    if "restart" in text:
        return "pm2 restart all"
    return "pm2 list"


def execute_plan(plan: dict[str, Any], *, host: str, api_key: str | None, model: str) -> dict[str, Any]:
    route = plan["route"]
    workspace = plan["workspace"]
    prompt = plan["prompt"]
    intent = plan["intent"]["intent"]

    if route in {"litellm-reasoner", "repo-context"}:
        include = infer_workspace_context(workspace, intent)
        result = ask_model(
            prompt,
            workspace=workspace,
            host=host,
            api_key=api_key,
            model=model,
            include=include,
        )
        return {
            "status": "completed",
            "route": route,
            "plan": plan,
            "result": result,
        }

    if route == "pm2":
        command = _pm2_command(prompt)
        result = run_shell_command(command, workspace)
        return {
            "status": "completed",
            "route": route,
            "plan": plan,
            "result": result,
        }

    return {
        "status": "planned_only",
        "route": route,
        "plan": plan,
        "result": {
            "content": (
                f"Phase 1 planned this request for the `{route}` tool domain, "
                "but that adapter is not wired for live execution yet. "
                "Use `plan` to inspect the route or explicit task/flow commands for mutations."
            ),
            "workspace": workspace,
            "model": model,
        },
    }


def infer_workspace_context(workspace: str | Path, intent: str) -> list[str]:
    root = Path(workspace).resolve()
    candidates: list[str] = []
    if intent == "repo_analysis":
        for relative in ("README.md", ".litellm/README.md", ".litellm/tasks/repair.yaml", ".litellm/tasks/flow-hardening.yaml"):
            if (root / relative).exists():
                candidates.append(relative)
    elif intent == "workflow_editing":
        for relative in (".litellm/tasks/repair.yaml", ".litellm/tasks/flow-hardening.yaml"):
            if (root / relative).exists():
                candidates.append(relative)
    return candidates
