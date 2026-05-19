"""Agent target definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import SkillhostError


@dataclass(frozen=True)
class Agent:
    name: str
    user_target: Path
    project_target: Path


AGENTS: dict[str, Agent] = {
    "codex": Agent("codex", Path.home() / ".agents" / "skills", Path(".agents") / "skills"),
    "claude": Agent("claude", Path.home() / ".claude" / "skills", Path(".claude") / "skills"),
    "opencode": Agent(
        "opencode",
        Path.home() / ".config" / "opencode" / "skills",
        Path(".opencode") / "skills",
    ),
}
DEFAULT_AGENT_NAMES = ["codex", "claude", "opencode"]


def get_agents(names: list[str] | None = None) -> list[Agent]:
    selected = names or DEFAULT_AGENT_NAMES
    unknown = [name for name in selected if name not in AGENTS]
    if unknown:
        raise SkillhostError(f"Unknown agent(s): {', '.join(unknown)}")
    return [AGENTS[name] for name in selected]
