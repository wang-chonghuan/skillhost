"""Project matching helpers."""

from __future__ import annotations

from pathlib import Path

from . import config
from .errors import SkillhostError
from .git_utils import get_origin_url, get_repo_root, normalize_git_url


def current_project_context(project: str | None = None, cwd: str | Path = ".") -> tuple[str, Path]:
    root = get_repo_root(cwd)
    origin = normalize_git_url(get_origin_url(root))
    cfg = config.load_config()
    projects = cfg.get("projects", {})
    if project:
        pdata = projects.get(project)
        if pdata is None:
            raise SkillhostError(f"Project '{project}' is not registered")
        remotes = pdata.get("remotes", [])
        if remotes and origin not in remotes:
            raise SkillhostError(f"Current repository ({origin}) does not match registered project '{project}'")
        return project, root
    matched = config.get_project_by_remote(origin)
    if not matched:
        raise SkillhostError(
            "Current directory is not a registered project. Run: skillhost project register <name> --git <repo-url>"
        )
    return matched, root
