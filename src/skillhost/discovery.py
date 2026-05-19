"""Skill discovery and simple SKILL.md frontmatter parsing."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .errors import SkillhostError

NAME_RE = re.compile(r"^[a-z0-9-]+$")
EXCLUDED_FLAT_DIRS = {
    ".git",
    "tests",
    "docs",
    "examples",
    "scripts",
    "references",
    "assets",
    "__pycache__",
}


@dataclass(frozen=True)
class Skill:
    name: str
    source_path: Path
    repo_name: str
    scope: str
    project: str | None = None
    description: str | None = None


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = skill_md.read_text(errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and value:
            data[key] = value
    return {}


def _skill_from_path(path: Path, fallback_name: str, repo_name: str, scope: str, project: str | None) -> Skill:
    fm = parse_frontmatter(path / "SKILL.md")
    name = fm.get("name", fallback_name).strip()
    if name != fallback_name and fm.get("name"):
        print(
            f"Warning: skill directory name '{fallback_name}' differs from frontmatter name '{name}'",
            file=sys.stderr,
        )
    if not NAME_RE.fullmatch(name):
        raise SkillhostError(
            f"Invalid skill name '{name}' in {path / 'SKILL.md'}; use lowercase letters, digits, and hyphens only"
        )
    return Skill(
        name=name,
        source_path=path.resolve(),
        repo_name=repo_name,
        scope=scope,
        project=project,
        description=fm.get("description"),
    )


def discover_skills_in_repo(
    repo_path: str | Path, repo_name: str, scope: str, project: str | None = None
) -> list[Skill]:
    repo = Path(repo_path)
    skills: list[Skill] = []
    if (repo / "SKILL.md").is_file():
        return [_skill_from_path(repo, repo_name, repo_name, scope, project)]

    skills_dir = repo / "skills"
    if skills_dir.is_dir():
        for child in sorted(skills_dir.iterdir()):
            if child.is_dir() and (child / "SKILL.md").is_file():
                skills.append(_skill_from_path(child, child.name, repo_name, scope, project))
        return skills

    for child in sorted(repo.iterdir() if repo.exists() else []):
        if not child.is_dir() or child.name.startswith(".") or child.name in EXCLUDED_FLAT_DIRS:
            continue
        if (child / "SKILL.md").is_file():
            skills.append(_skill_from_path(child, child.name, repo_name, scope, project))
    return skills


def discover_repos(repos_dir: str | Path, scope: str, project: str | None = None) -> list[Skill]:
    root = Path(repos_dir)
    all_skills: list[Skill] = []
    if not root.exists():
        return []
    for repo in sorted(p for p in root.iterdir() if p.is_dir()):
        all_skills.extend(discover_skills_in_repo(repo, repo.name, scope, project))
    return all_skills
