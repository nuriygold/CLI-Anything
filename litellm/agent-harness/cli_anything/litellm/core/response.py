"""Response formatting helpers for agent-style commands."""

from __future__ import annotations

from typing import Any


def plan_summary(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "intent": plan["intent"]["intent"],
        "confidence": plan["intent"]["confidence"],
        "mutating": plan["intent"]["mutating"],
        "route": plan["route"],
        "tool_candidates": plan["tool_candidates"],
        "requires_confirmation": plan["requires_confirmation"],
        "rationale": plan["rationale"],
        "limitations": plan["limitations"],
        "next_actions": plan["next_actions"],
    }


def execution_summary(execution: dict[str, Any]) -> dict[str, Any]:
    result = execution["result"]
    if isinstance(result, dict):
        content = execution.get("content") or result.get("content", "") or result.get("stdout", "") or result.get("stderr", "")
    else:
        content = execution.get("content") or str(result)
    return {
        "status": execution["status"],
        "route": execution["route"],
        "intent": execution["plan"]["intent"]["intent"],
        "content": content,
        "limitations": execution["plan"]["limitations"],
    }


def shell_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "command": result["command"],
        "returncode": result["returncode"],
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
    }
