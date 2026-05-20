from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__, config, paths
from .discovery import Skill, discover_repos
from .errors import GIT_ERROR, INTERNAL_ERROR, USER_ERROR, GitError, SkillhostError
from .git_utils import clone_repo, derive_repo_name, is_git_repo, pull_ff_only
from .linking import MANIFEST, link_skills, load_manifest, unlink_scope
from .projects import current_project_context

AGENT_CHOICES = ["codex", "claude", "opencode"]


def _selected_scope(project: str | None) -> tuple[str, Path, str | None]:
    if project:
        config.require_project(project)
        return "project", config.project_repos_path_from_config(project), project
    return "user", config.user_repos_path_from_config(), None


def _repo_records(scope: str, project: str | None) -> dict[str, dict]:
    cfg = config.load_config()
    if scope == "user":
        return cfg.get("user_repos", {})
    return cfg.get("projects", {}).get(project or "", {}).get("repos", {})


def _project_root(project: str) -> Path:
    _name, root = current_project_context(project)
    return root


def _target_entries(scope: str, project: str | None, agent_name: str | None) -> list[tuple[str, Path]]:
    agents = config.get_registered_agents()
    if agent_name:
        if agent_name not in agents or not agents[agent_name].get("enabled", True):
            raise SkillhostError(f"Agent not registered: {agent_name}")
        selected = {agent_name: agents[agent_name]}
    else:
        selected = {name: data for name, data in agents.items() if data.get("enabled", True)}
    entries: list[tuple[str, Path]] = []
    for name, data in selected.items():
        if scope == "user":
            entries.append((name, Path(data["user_dir"])))
        else:
            project_dir = data.get("project_dir")
            if not project_dir:
                continue
            entries.append((name, _project_root(project or "") / project_dir))
    return entries


def _targets(scope: str, project: str | None, agent_name: str | None) -> dict[str, Path]:
    return {name: path for name, path in _target_entries(scope, project, agent_name)}


def _discover_scope(scope: str, repo_dir: Path, project: str | None) -> list[Skill]:
    return discover_repos(repo_dir, scope, project)


def _select_skills(skills: list[Skill], repo_name: str | None) -> list[Skill]:
    if repo_name is None:
        return skills
    return [skill for skill in skills if skill.repo_name == repo_name]


def _all_repo_names(scope: str, project: str | None) -> list[str]:
    return sorted(_repo_records(scope, project))


def _require_repo_name(name: str | None, command: str) -> str:
    if not name:
        raise SkillhostError(f"{command} requires <repo-name>.")
    return name


def _print_skills(skills: list[Skill]) -> None:
    if not skills:
        print("No skills found.")
        return
    for skill in skills:
        location = f"project:{skill.project}" if skill.project else "user"
        print(f"{skill.repo_name}\t{skill.name}\t{location}")


def _doctor_target(target: Path) -> int:
    issues = 0
    manifest_path = target / MANIFEST
    if manifest_path.exists():
        manifest = load_manifest(target)
        for name, record in manifest.get("links", {}).items():
            source = record.get("source")
            dest = target / name
            if source and not Path(source).exists():
                print(f"manifest source missing: {dest} -> {source}")
                issues += 1
            if dest.is_symlink() and not dest.exists():
                print(f"broken symlink: {dest}")
                issues += 1
    if target.exists():
        for child in target.iterdir():
            if child.is_symlink() and not child.exists():
                print(f"broken symlink: {child}")
                issues += 1
    return issues


def _relink_selected(scope: str, project: str | None, repo_name: str | None, agent_name: str | None) -> int:
    base_dir = config.project_repos_path_from_config(project) if scope == "project" else config.user_repos_path_from_config()
    names = _all_repo_names(scope, project)
    if repo_name and repo_name not in names:
        raise SkillhostError(f"Repo not found in selected scope: {repo_name}")
    skills = _select_skills(_discover_scope(scope, base_dir, project), repo_name)
    failures = link_skills(skills, _targets(scope, project, agent_name), scope, project=project)
    return USER_ERROR if failures else 0


def cmd_init(_args: argparse.Namespace) -> int:
    config.ensure_default_config()
    return 0


def cmd_register(args: argparse.Namespace) -> int:
    if bool(args.project) == bool(args.agent):
        raise SkillhostError("Use exactly one of --project or --agent.")
    if args.project:
        if not args.git:
            raise SkillhostError("register --project requires --git.")
        config.register_project(args.project, args.git)
        print(f"Registered project '{args.project}'.")
        return 0
    if args.git:
        raise SkillhostError("--git is only valid with --project.")
    config.register_agent(args.agent, args.user_dir, args.project_dir)
    print(f"Registered agent '{args.agent}'.")
    print("Run `skillhost relink` to refresh user-level links.")
    return 0


def cmd_unregister(args: argparse.Namespace) -> int:
    if bool(args.project) == bool(args.agent):
        raise SkillhostError("Use exactly one of --project or --agent.")
    if args.project:
        config.unregister_project(args.project)
        print(f"Unregistered project '{args.project}'.")
        return 0
    config.unregister_agent(args.agent)
    print(f"Unregistered agent '{args.agent}'.")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    scope, base_dir, project = _selected_scope(args.project)
    repo_name = args.name or derive_repo_name(args.skill_git_repo)
    repo_records = _repo_records(scope, project)
    if repo_name in repo_records:
        raise SkillhostError(f"Repo already registered in selected scope: {repo_name}")
    dest = base_dir / repo_name
    if dest.exists():
        raise SkillhostError(f"Clone target already exists: {dest}")
    clone_repo(args.skill_git_repo, dest)
    config.register_repo(scope, repo_name, args.skill_git_repo, dest, project)
    print(f"Added repo '{repo_name}'.")
    if scope == "user":
        return _relink_selected(scope, project, repo_name, None)
    try:
        return _relink_selected(scope, project, repo_name, None)
    except SkillhostError:
        print(f"Added project skill repo for {project}.")
        print("Run inside the project checkout:")
        print(f"  skillhost relink --project {project}")
        return 0


def cmd_update(args: argparse.Namespace) -> int:
    scope, base_dir, project = _selected_scope(args.project)
    names = _all_repo_names(scope, project)
    if args.repo_name:
        if args.repo_name not in names:
            raise SkillhostError(f"Repo not found in selected scope: {args.repo_name}")
        names = [args.repo_name]
    for name in names:
        pull_ff_only(base_dir / name)
        print(f"Updated {name}")
    if scope == "user":
        return _relink_selected(scope, project, args.repo_name, args.agent)
    try:
        return _relink_selected(scope, project, args.repo_name, args.agent)
    except SkillhostError:
        print("Updated project skill repo(s).")
        print("Run inside the project checkout:")
        print(f"  skillhost relink --project {project}")
        return 0


def cmd_remove(args: argparse.Namespace) -> int:
    scope, base_dir, project = _selected_scope(args.project)
    name = _require_repo_name(args.repo_name, "remove")
    if name not in _all_repo_names(scope, project):
        raise SkillhostError(f"Repo not found in selected scope: {name}")
    removed = 0
    if scope == "user":
        for agent_name, target in _targets(scope, project, None).items():
            removed += unlink_scope({agent_name: target}, scope, project=project, repo_name=name)
    else:
        try:
            for agent_name, target in _targets(scope, project, None).items():
                removed += unlink_scope({agent_name: target}, scope, project=project, repo_name=name)
        except SkillhostError:
            pass
    shutil.rmtree(base_dir / name)
    config.remove_repo(scope, name, project)
    print(f"Removed repo '{name}' and unlinked {removed} skill(s).")
    return 0


def cmd_relink(args: argparse.Namespace) -> int:
    scope, _base_dir, project = _selected_scope(args.project)
    return _relink_selected(scope, project, args.repo_name, args.agent)


def cmd_unlink(args: argparse.Namespace) -> int:
    scope, _base_dir, project = _selected_scope(args.project)
    if not args.repo_name and not args.all:
        raise SkillhostError("Refusing to unlink all links implicitly. Use --all.")
    removed = 0
    for agent_name, target in _target_entries(scope, project, args.agent):
        removed += unlink_scope({agent_name: target}, scope, project=project, repo_name=args.repo_name)
    print(f"Unlinked {removed} skill(s).")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    scope, base_dir, project = _selected_scope(args.project)
    _print_skills(_discover_scope(scope, base_dir, project))
    return 0


def cmd_projects(_args: argparse.Namespace) -> int:
    for name, pdata in config.load_config().get("projects", {}).items():
        remotes = ", ".join(pdata.get("remotes", []))
        print(f"{name}\t{remotes}")
    return 0


def cmd_agents(_args: argparse.Namespace) -> int:
    for name, data in config.get_registered_agents().items():
        project_dir = data.get("project_dir") or ""
        print(f"{name}\t{data['user_dir']}\t{project_dir}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    issues = 0
    cfg = config.load_config()
    if cfg.get("version") != 1:
        print("unexpected config version")
        issues += 1

    scope, base_dir, project = _selected_scope(args.project)
    repo_records = _repo_records(scope, project)
    skills = _discover_scope(scope, base_dir, project)

    for repo_name, record in repo_records.items():
        repo_path = Path(record["path"])
        if not repo_path.exists():
            print(f"repo missing: {repo_path}")
            issues += 1
        elif not is_git_repo(repo_path):
            print(f"repo is not a git repo: {repo_path}")
            issues += 1

    seen: set[str] = set()
    for skill in skills:
        if skill.name in seen:
            print(f"name conflict: {skill.name}")
            issues += 1
        seen.add(skill.name)

    try:
        targets = _target_entries(scope, project, None)
    except SkillhostError as exc:
        print(exc)
        return USER_ERROR
    for _name, target in targets:
        issues += _doctor_target(target)

    if issues == 0:
        print("OK")
        return 0
    return USER_ERROR


def cmd_config(_args: argparse.Namespace) -> int:
    print(paths.config_path())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillhost")
    parser.add_argument("--version", action="version", version=f"skillhost {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)

    p = sub.add_parser("register")
    p.add_argument("--project")
    p.add_argument("--git")
    p.add_argument("--agent")
    p.add_argument("--user-dir")
    p.add_argument("--project-dir")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("unregister")
    p.add_argument("--project")
    p.add_argument("--agent")
    p.set_defaults(func=cmd_unregister)

    p = sub.add_parser("add")
    p.add_argument("skill_git_repo")
    p.add_argument("--project")
    p.add_argument("--name")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("update")
    p.add_argument("repo_name", nargs="?")
    p.add_argument("--project")
    p.add_argument("--agent", choices=AGENT_CHOICES)
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("remove")
    p.add_argument("repo_name")
    p.add_argument("--project")
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("relink")
    p.add_argument("repo_name", nargs="?")
    p.add_argument("--project")
    p.add_argument("--agent", choices=AGENT_CHOICES)
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_relink)

    p = sub.add_parser("unlink")
    p.add_argument("repo_name", nargs="?")
    p.add_argument("--project")
    p.add_argument("--agent", choices=AGENT_CHOICES)
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_unlink)

    p = sub.add_parser("list")
    p.add_argument("--project")
    p.set_defaults(func=cmd_list)

    sub.add_parser("projects").set_defaults(func=cmd_projects)
    sub.add_parser("agents").set_defaults(func=cmd_agents)

    p = sub.add_parser("doctor")
    p.add_argument("--project")
    p.set_defaults(func=cmd_doctor)

    sub.add_parser("config").set_defaults(func=cmd_config)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except GitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return GIT_ERROR
    except SkillhostError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        return USER_ERROR
    except Exception as exc:  # pragma: no cover
        print(f"internal error: {exc}", file=sys.stderr)
        return INTERNAL_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
