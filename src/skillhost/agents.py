"""Agent target definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import SkillhostError


@dataclass(frozen=True)
class Agent:
    name: str
    user_target: Path
    project_target: Path | None = None


def _default_agent_map() -> dict[str, Agent]:
    home = Path.home()
    return {
        "codex": Agent("codex", home / ".agents" / "skills", Path(".agents") / "skills"),
        "claude": Agent("claude", home / ".claude" / "skills", Path(".claude") / "skills"),
        "opencode": Agent(
            "opencode",
            home / ".config" / "opencode" / "skills",
            Path(".opencode") / "skills",
        ),
        "openclaw": Agent("openclaw", home / ".openclaw" / "skills"),
        "hermes": Agent("hermes", home / ".hermes" / "skills"),
    }


AGENTS: dict[str, Agent] = _default_agent_map()
DEFAULT_AGENT_NAMES = ["codex", "claude", "opencode", "openclaw", "hermes"]


def get_agents(names: list[str] | None = None) -> list[Agent]:
    selected = names or DEFAULT_AGENT_NAMES
    unknown = [name for name in selected if name not in AGENTS]
    if unknown:
        raise SkillhostError(f"Unknown agent(s): {', '.join(unknown)}")
    return [AGENTS[name] for name in selected]
