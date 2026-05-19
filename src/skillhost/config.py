"""Configuration loading, writing, and project registration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # pragma: no cover - availability depends on interpreter
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

import os

from . import paths
from .agents import DEFAULT_AGENT_NAMES
from .git_utils import normalize_git_url


def _parse_simple_value(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [_parse_simple_value(part.strip()) for part in inner.split(",")]
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if raw in {"true", "false"}:
        return raw == "true"
    try:
        return int(raw)
    except ValueError:
        return raw


def _load_simple_toml(path: Path) -> dict[str, Any]:
    """Tiny TOML reader for skillhost's own simple config schema on Python 3.10."""
    root: dict[str, Any] = {}
    current = root
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].split("."):
                current = current.setdefault(part, {})
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            current[key.strip()] = _parse_simple_value(value)
    return root


def _default_user_repos_value() -> str:
    if os.environ.get("SKILLHOST_HOME"):
        return str(paths.user_repos_dir())
    return "~/.skillhost/user_repos"


def _default_project_repos_value(project: str) -> str:
    if os.environ.get("SKILLHOST_HOME"):
        return str(paths.project_repos_dir(project))
    return f"~/.skillhost/project_repos/{project}"


def default_config() -> dict[str, Any]:
    return {
        "version": 1,
        "agents": {"enabled": list(DEFAULT_AGENT_NAMES)},
        "user": {"repos_dir": _default_user_repos_value()},
        "projects": {},
    }


def ensure_default_config() -> dict[str, Any]:
    paths.ensure_base_dirs()
    cfg_path = paths.config_path()
    if not cfg_path.exists():
        cfg = default_config()
        save_config(cfg)
        return cfg
    return load_config()


def load_config() -> dict[str, Any]:
    paths.ensure_base_dirs()
    cfg_path = paths.config_path()
    if not cfg_path.exists():
        return ensure_default_config()
    if tomllib is not None:
        with cfg_path.open("rb") as fh:
            data = tomllib.load(fh)
    else:
        data = _load_simple_toml(cfg_path)
    cfg = default_config()
    cfg.update(data)
    cfg.setdefault("agents", {}).setdefault("enabled", list(DEFAULT_AGENT_NAMES))
    cfg.setdefault("user", {}).setdefault("repos_dir", _default_user_repos_value())
    cfg.setdefault("projects", {})
    return cfg


def _toml_value(value: Any) -> str:
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    raise TypeError(f"Unsupported TOML value: {value!r}")


def save_config(cfg: dict[str, Any]) -> None:
    paths.ensure_base_dirs()
    lines: list[str] = [f"version = {_toml_value(int(cfg.get('version', 1)))}", ""]
    agents = cfg.get("agents", {})
    lines.append("[agents]")
    lines.append(f"enabled = {_toml_value(list(agents.get('enabled', DEFAULT_AGENT_NAMES)))}")
    lines.append("")
    user = cfg.get("user", {})
    lines.append("[user]")
    lines.append(f"repos_dir = {_toml_value(str(user.get('repos_dir', _default_user_repos_value())))}")
    lines.append("")
    for project, pdata in sorted(cfg.get("projects", {}).items()):
        lines.append(f"[projects.{project}]")
        lines.append(f"remotes = {_toml_value(list(pdata.get('remotes', [])))}")
        lines.append(f"repos_dir = {_toml_value(str(pdata.get('repos_dir', _default_project_repos_value(project))))}")
        lines.append("")
    paths.config_path().write_text("\n".join(lines), encoding="utf-8")


def register_project(project: str, git_url: str) -> dict[str, Any]:
    cfg = load_config()
    normalized = normalize_git_url(git_url)
    projects = cfg.setdefault("projects", {})
    pdata = projects.setdefault(
        project,
        {"remotes": [], "repos_dir": _default_project_repos_value(project)},
    )
    pdata.setdefault("repos_dir", _default_project_repos_value(project))
    remotes = pdata.setdefault("remotes", [])
    if normalized not in remotes:
        remotes.append(normalized)
    Path(pdata["repos_dir"]).expanduser().mkdir(parents=True, exist_ok=True)
    save_config(cfg)
    return cfg


def get_project(project: str) -> dict[str, Any] | None:
    return load_config().get("projects", {}).get(project)


def get_project_by_remote(normalized_remote: str) -> str | None:
    for project, pdata in load_config().get("projects", {}).items():
        if normalized_remote in pdata.get("remotes", []):
            return project
    return None


def list_projects() -> dict[str, Any]:
    return load_config().get("projects", {})


def user_repos_path_from_config(cfg: dict[str, Any] | None = None) -> Path:
    cfg = cfg or load_config()
    return Path(cfg.get("user", {}).get("repos_dir", _default_user_repos_value())).expanduser()


def project_repos_path_from_config(project: str, cfg: dict[str, Any] | None = None) -> Path:
    cfg = cfg or load_config()
    pdata = cfg.get("projects", {}).get(project, {})
    return Path(pdata.get("repos_dir", _default_project_repos_value(project))).expanduser()
