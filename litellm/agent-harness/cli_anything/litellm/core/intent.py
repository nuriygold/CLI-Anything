"""Intent classification for agent-style CLI requests."""

from __future__ import annotations

from typing import Any


INTENT_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("system_diagnostics", ("battery", "cpu", "memory", "disk", "fan", "power", "usage", "draining")),
    ("process_runtime", ("restart", "stop", "start", "server", "logs", "deploy", "process", "service")),
    ("browser_inspection", ("browser", "page", "site", "screen", "login", "click", "open the app")),
    ("workflow_editing", ("workflow", "n8n", "dify", "loop", "orchestration", "retry")),
    ("repo_analysis", ("repo", "repository", "codebase", "bug", "inspect this repo", "what changed")),
    ("research", ("look up", "search", "docs", "documentation", "error meaning", "what does this error")),
    ("memory", ("remember", "note", "save this", "recall", "knowledge base")),
    ("patch_generation", ("fix", "patch", "edit", "rewrite", "update this file", "apply")),
]

MUTATING_INTENTS = {"patch_generation", "workflow_editing"}

PROCESS_RUNTIME_MUTATING_KEYWORDS = ("restart", "stop", "start", "kill", "reload", "deploy", "restart", "uninstall")


def classify_intent(prompt: str) -> dict[str, Any]:
    text = prompt.strip().lower()
    if not text:
        return {
            "intent": "general_assistance",
            "confidence": 0.0,
            "mutating": False,
            "matched_keywords": [],
        }

    best_intent = "general_assistance"
    best_matches: list[str] = []
    for intent, keywords in INTENT_KEYWORDS:
        matches = [keyword for keyword in keywords if keyword in text]
        if len(matches) > len(best_matches):
            best_intent = intent
            best_matches = matches

    confidence = min(0.95, 0.35 + 0.15 * len(best_matches)) if best_matches else 0.3
    mutating = best_intent in MUTATING_INTENTS
    if best_intent == "process_runtime":
        mutating = any(keyword in text for keyword in PROCESS_RUNTIME_MUTATING_KEYWORDS)
    return {
        "intent": best_intent,
        "confidence": confidence,
        "mutating": mutating,
        "matched_keywords": best_matches,
    }
