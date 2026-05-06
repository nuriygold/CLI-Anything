"""Prompt planning for agent-style CLI workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cli_anything.litellm.core.intent import classify_intent


TOOL_CANDIDATES = {
    "system_diagnostics": ["system"],
    "process_runtime": ["pm2", "iterm2"],
    "browser_inspection": ["browser"],
    "workflow_editing": ["n8n", "dify-workflow", "litellm-task-engine"],
    "repo_analysis": ["litellm-reasoner", "repo-context"],
    "research": ["exa"],
    "memory": ["chromadb", "obsidian"],
    "patch_generation": ["litellm-task-engine"],
    "general_assistance": ["litellm-reasoner"],
}


def build_plan(prompt: str, *, workspace: str | Path, mode: str = "assist") -> dict[str, Any]:
    classification = classify_intent(prompt)
    intent = classification["intent"]
    tool_candidates = TOOL_CANDIDATES[intent]
    workspace_path = str(Path(workspace).resolve())
    execution_mode = "explain_only" if classification["mutating"] else "answer"
    requires_confirmation = classification["mutating"] and mode != "act"
    limitations: list[str] = []
    if classification["mutating"]:
        limitations.append("Natural-language mutating requests are planned conservatively in phase 1.")
        limitations.append("Use explicit `task run` or `flow run` for fully automated patch loops.")
    if intent in {"system_diagnostics", "process_runtime", "browser_inspection", "research", "memory"}:
        limitations.append("Phase 1 identifies the right tool domain but does not execute external tool adapters yet.")

    rationale = {
        "system_diagnostics": "The prompt asks about system behavior or resource consumption.",
        "process_runtime": "The prompt appears to target live processes, logs, or running services.",
        "browser_inspection": "The prompt references an app/page inspection workflow.",
        "workflow_editing": "The prompt appears to target workflows, loops, or orchestration definitions.",
        "repo_analysis": "The prompt asks for codebase or repository understanding.",
        "research": "The prompt appears to require external information lookup or documentation search.",
        "memory": "The prompt appears to require persistent note or memory storage/retrieval.",
        "patch_generation": "The prompt asks for a code or file mutation.",
        "general_assistance": "The prompt is best handled as a general reasoning request.",
    }[intent]

    return {
        "prompt": prompt,
        "workspace": workspace_path,
        "mode": mode,
        "intent": classification,
        "tool_candidates": tool_candidates,
        "route": tool_candidates[0],
        "execution_mode": execution_mode,
        "requires_confirmation": requires_confirmation,
        "rationale": rationale,
        "limitations": limitations,
        "next_actions": suggest_next_actions(intent),
    }


def suggest_next_actions(intent: str) -> list[str]:
    suggestions = {
        "system_diagnostics": ["Add system diagnostics adapters in Phase 3.", "Gather local process and power data before answering."],
        "process_runtime": ["Use runtime adapters like pm2 or terminal control in later phases.", "Collect logs before proposing restarts."],
        "browser_inspection": ["Open and inspect the app via a browser adapter in Phase 4."],
        "workflow_editing": ["Use explicit flow commands or workflow adapters for real edits.", "Inspect workflow definitions before mutating them."],
        "repo_analysis": ["Read relevant files from the workspace and summarize findings."],
        "research": ["Use a search adapter to retrieve current docs or references."],
        "memory": ["Store or retrieve semantic memory once a memory adapter is wired in during Phase 2."],
        "patch_generation": ["Translate the prompt into a repo-local task YAML if mutation is required."],
        "general_assistance": ["Answer directly with the LiteLLM reasoner."],
    }
    return suggestions[intent]
