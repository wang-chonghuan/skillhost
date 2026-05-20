"""Configuration loading and writing for skillhost."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import agents as agents_module
from .errors import SkillhostError
from .git_utils import get_origin_url, is_git_repo, normalize_git_url
from .paths import config_path, ensure_base_dirs, project_repos_dir, skillhost_home, user_repos_dir


def _default_agents() -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    for name, agent in agents_module._default_agent_map().items():
        data[name] = {
            "enabled": True,
            "user_dir": str(agent.user_target.expanduser().resolve()),
            "project_dir": str(agent.project_target) if agent.project_target else "",
            "builtin": True,
        }
    return data


def default_config() -> dict[str, Any]:
    home = skillhost_home()
    return {
        "version": 1,
        "home": str(home),
        "agents": _default_agents(),
        "user_repos": {},
        "projects": {},
    }


def _normalize_repo_record(record: dict[str, Any]) -> dict[str, str]:
    url = record.get("url") or record.get("git_url")
    normalized_url = record.get("normalized_url") or record.get("normalized_git_url")
    path = record.get("path") or record.get("local_path")
    normalized: dict[str, str] = {}
    if url is not None:
        normalized["url"] = str(url)
    if normalized_url is not None:
        normalized["normalized_url"] = str(normalized_url)
    if path is not None:
        normalized["path"] = str(Path(path).expanduser().resolve())
    return normalized


def _migrate_config(data: dict[str, Any]) -> dict[str, Any]:
    migrated = default_config()
    migrated["version"] = int(data.get("version", 1))
    migrated["home"] = str(skillhost_home())
    migrated["agents"] = data.get("agents", _default_agents())

    for name, record in data.get("user_repos", {}).items():
        migrated["user_repos"][name] = _normalize_repo_record(record)

    projects = data.get("projects", {})
    project_repos = data.get("project_repos", {})
    for project_name, pdata in projects.items():
        remotes = pdata.get("remotes")
        normalized = pdata.get("normalized_git_url")
        git = pdata.get("git")
        if remotes:
            normalized_list = [str(item) for item in remotes]
        elif normalized:
            normalized_list = [str(normalized)]
        elif git:
            normalized_list = [normalize_git_url(str(git))]
        else:
            normalized_list = []

        repos = {
            name: _normalize_repo_record(record) for name, record in pdata.get("repos", {}).items()
        }
        for name, record in project_repos.get(project_name, {}).items():
            repos[name] = _normalize_repo_record(record)

        migrated["projects"][project_name] = {
            "remotes": normalized_list,
            "repos": repos,
        }
    return migrated


def _normalize_config(data: dict[str, Any]) -> dict[str, Any]:
    cfg = _migrate_config(data)
    cfg["home"] = str(skillhost_home())
    agents = cfg.setdefault("agents", {})
    for name, defaults in _default_agents().items():
        current = agents.setdefault(name, defaults)
        current.setdefault("enabled", True)
        current.setdefault("user_dir", defaults["user_dir"])
        current.setdefault("project_dir", defaults["project_dir"])
        current.setdefault("builtin", defaults["builtin"])
        current["user_dir"] = str(Path(current["user_dir"]).expanduser().resolve())

    cfg.setdefault("user_repos", {})
    for name, record in list(cfg["user_repos"].items()):
        cfg["user_repos"][name] = _normalize_repo_record(record)

    cfg.setdefault("projects", {})
    for project_name, pdata in list(cfg["projects"].items()):
        pdata.setdefault("remotes", [])
        pdata.setdefault("repos", {})
        pdata["remotes"] = [str(item) for item in pdata["remotes"]]
        pdata["repos"] = {
            name: _normalize_repo_record(record) for name, record in pdata.get("repos", {}).items()
        }
    return cfg


def ensure_default_config() -> dict[str, Any]:
    ensure_base_dirs()
    cfg_path = config_path()
    if not cfg_path.exists():
        cfg = default_config()
        save_config(cfg)
        return cfg
    return load_config()


def load_config() -> dict[str, Any]:
    ensure_base_dirs()
    cfg_path = config_path()
    if not cfg_path.exists():
        return ensure_default_config()
    return _normalize_config(json.loads(cfg_path.read_text(encoding="utf-8")))


def save_config(cfg: dict[str, Any]) -> None:
    ensure_base_dirs()
    normalized = _normalize_config(cfg)
    config_path().write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def user_repos_path_from_config() -> Path:
    return user_repos_dir()


def project_repos_path_from_config(project: str) -> Path:
    return project_repos_dir(project)


def get_registered_agents() -> dict[str, dict[str, Any]]:
    return load_config().get("agents", {})


def register_agent(name: str, user_dir: str | None, project_dir: str | None = None) -> None:
    if not user_dir and not project_dir:
        raise SkillhostError("register --agent requires --user-dir or --project-dir.")
    cfg = load_config()
    existing = cfg.setdefault("agents", {}).get(name, {})
    cfg["agents"][name] = {
        "enabled": True,
        "user_dir": str(Path(user_dir or existing.get("user_dir", Path.home() / f'.{name}' / 'skills')).expanduser().resolve()),
        "project_dir": project_dir if project_dir is not None else existing.get("project_dir"),
        "builtin": False,
    }
    save_config(cfg)


def unregister_agent(name: str) -> None:
    cfg = load_config()
    if name not in cfg.get("agents", {}):
        raise SkillhostError(f"Agent not registered: {name}")
    del cfg["agents"][name]
    save_config(cfg)


def _normalize_project_remote(git_url: str) -> str:
    candidate = Path(git_url).expanduser()
    if candidate.exists() and is_git_repo(candidate):
        try:
            return _normalize_repo_url(git_url, candidate)
        except SkillhostError:
            return str(candidate.resolve())
    return normalize_git_url(git_url)


def register_project(project: str, git_url: str) -> None:
    cfg = load_config()
    cfg.setdefault("projects", {})[project] = {
        "remotes": [_normalize_project_remote(git_url)],
        "repos": cfg.get("projects", {}).get(project, {}).get("repos", {}),
    }
    project_repos_path_from_config(project).mkdir(parents=True, exist_ok=True)
    save_config(cfg)


def unregister_project(project: str) -> None:
    cfg = load_config()
    if project not in cfg.get("projects", {}):
        raise SkillhostError(f"Project not registered: {project}")
    del cfg["projects"][project]
    save_config(cfg)


def list_projects() -> list[str]:
    return sorted(load_config().get("projects", {}))


def require_project(project: str | None) -> dict[str, Any]:
    if not project:
        raise SkillhostError("--project <name> is required.")
    cfg = load_config()
    pdata = cfg.get("projects", {}).get(project)
    if pdata is None:
        raise SkillhostError(f"Project not registered: {project}")
    return pdata


def project_repo_records(project: str) -> dict[str, dict[str, str]]:
    return load_config().get("projects", {}).get(project, {}).get("repos", {})


def _normalize_repo_url(git_url: str, local_path: Path) -> str:
    if is_git_repo(local_path):
        origin = get_origin_url(local_path)
        try:
            return normalize_git_url(origin)
        except SkillhostError:
            return str(Path(origin).resolve())
    return normalize_git_url(git_url)


def register_repo(scope: str, repo_name: str, git_url: str, local_path: Path, project: str | None = None) -> None:
    cfg = load_config()
    record = {
        "url": git_url,
        "normalized_url": _normalize_repo_url(git_url, local_path),
        "path": str(local_path.resolve()),
    }
    if scope == "user":
        cfg.setdefault("user_repos", {})[repo_name] = record
    else:
        if not project:
            raise SkillhostError("project scope requires a project name")
        cfg.setdefault("projects", {}).setdefault(project, {"remotes": [], "repos": {}})
        cfg["projects"][project].setdefault("repos", {})[repo_name] = record
    save_config(cfg)


def remove_repo(scope: str, repo_name: str, project: str | None = None) -> None:
    cfg = load_config()
    if scope == "user":
        cfg.setdefault("user_repos", {}).pop(repo_name, None)
    else:
        if not project:
            raise SkillhostError("project scope requires a project name")
        cfg.setdefault("projects", {}).setdefault(project, {"remotes": [], "repos": {}})
        cfg["projects"][project].setdefault("repos", {}).pop(repo_name, None)
    save_config(cfg)
