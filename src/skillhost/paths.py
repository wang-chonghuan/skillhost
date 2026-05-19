"""Path helpers for skillhost state and agent targets."""

from __future__ import annotations

import os
from pathlib import Path


def expand_path(value: str | Path) -> Path:
    return Path(value).expanduser()


def skillhost_home() -> Path:
    override = os.environ.get("SKILLHOST_HOME")
    return expand_path(override) if override else Path.home() / ".skillhost"


def config_path() -> Path:
    return skillhost_home() / "config.toml"


def user_repos_dir() -> Path:
    return skillhost_home() / "user_repos"


def project_repos_root() -> Path:
    return skillhost_home() / "project_repos"


def project_repos_dir(project: str) -> Path:
    return project_repos_root() / project


def state_dir() -> Path:
    return skillhost_home() / "state"


def locks_dir() -> Path:
    return skillhost_home() / "locks"


def ensure_base_dirs() -> None:
    for path in (skillhost_home(), user_repos_dir(), project_repos_root(), state_dir(), locks_dir()):
        path.mkdir(parents=True, exist_ok=True)
