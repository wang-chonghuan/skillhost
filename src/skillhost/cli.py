"""Argparse command-line interface for skillhost."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__, config, paths
from .agents import get_agents
from .discovery import discover_repos, discover_skills_in_repo
from .errors import GIT_ERROR, INTERNAL_ERROR, USER_ERROR, GitError, SkillhostError
from .git_utils import (
    clone_repo,
    derive_repo_name,
    get_origin_url,
    is_dirty,
    is_git_repo,
    normalize_git_url,
    pull_ff_only,
)
from .linking import MANIFEST, link_skills, load_manifest, unlink_scope
from .projects import current_project_context


def agent_targets(scope: str, agent_name: str | None, repo_root: Path | None = None) -> dict[str, Path]:
    names = [agent_name] if agent_name else config.load_config().get("agents", {}).get("enabled")
    agents = get_agents(names)
    targets: dict[str, Path] = {}
    for agent in agents:
        if scope == "user":
            targets[agent.name] = agent.user_target
        else:
            assert repo_root is not None
            targets[agent.name] = repo_root / agent.project_target
    return targets


def _check_target_manifest(target: Path) -> int:
    issues = 0
    if not target.exists():
        print(f"target missing (will be created when linking): {target}")
        return 0
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
    for child in target.iterdir():
        if child.is_symlink() and not child.exists():
            print(f"broken symlink: {child}")
            issues += 1
    return issues


def _report_skill_conflicts(skills) -> int:
    issues = 0
    names: dict[str, str] = {}
    for skill in skills:
        if skill.name in names:
            print(f"name conflict: {skill.name} in {names[skill.name]} and {skill.repo_name}")
            issues += 1
        names[skill.name] = skill.repo_name
    return issues


def _ensure_clone_dest(url: str, base_dir: Path, name: str | None) -> tuple[str, Path, bool]:
    repo_name = name or derive_repo_name(url)
    dest = base_dir / repo_name
    if dest.exists():
        if is_git_repo(dest):
            try:
                same = normalize_git_url(get_origin_url(dest)) == normalize_git_url(url)
            except SkillhostError:
                same = False
            if same:
                return repo_name, dest, True
        raise SkillhostError(f"Clone target already exists and conflicts: {dest}. Pass --name.")
    return repo_name, dest, False


def user_add(args: argparse.Namespace) -> int:
    cfg = config.ensure_default_config()
    base = config.user_repos_path_from_config(cfg)
    base.mkdir(parents=True, exist_ok=True)
    repo_name, dest, exists = _ensure_clone_dest(args.git_repo, base, args.name)
    if exists:
        print(f"User repo '{repo_name}' already exists at {dest}")
    else:
        clone_repo(args.git_repo, dest, args.branch)
        print(f"Added user repo '{repo_name}' at {dest}")
    print("Run: skillhost user link")
    return 0


def _update_repos(base: Path, name: str | None = None) -> None:
    repos = [base / name] if name else sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []
    for repo in repos:
        if not repo.exists():
            raise SkillhostError(f"Repository not found: {repo}")
        if not is_git_repo(repo):
            raise SkillhostError(f"Not a git repository: {repo}")
        print(f"Updating {repo.name}")
        pull_ff_only(repo)


def user_update(args: argparse.Namespace) -> int:
    _update_repos(config.user_repos_path_from_config(), args.name)
    return 0


def user_link(args: argparse.Namespace) -> int:
    skills = discover_repos(config.user_repos_path_from_config(), "user")
    failures = link_skills(skills, agent_targets("user", args.agent), "user", dry_run=args.dry_run)
    return USER_ERROR if failures else 0


def user_unlink(args: argparse.Namespace) -> int:
    unlink_scope(agent_targets("user", args.agent), "user", dry_run=args.dry_run)
    return 0


def user_remove(args: argparse.Namespace) -> int:
    repo = config.user_repos_path_from_config() / args.name
    if not repo.exists():
        raise SkillhostError(f"User repo not found: {args.name}")
    if is_git_repo(repo) and is_dirty(repo) and not args.force:
        raise SkillhostError(f"Repository is dirty; use --force to remove: {repo}")
    unlink_scope(agent_targets("user", None), "user", repo_name=args.name)
    shutil.rmtree(repo)
    print(f"Removed user repo '{args.name}'")
    return 0


def user_list(_args: argparse.Namespace) -> int:
    base = config.user_repos_path_from_config()
    print("User repos:")
    for repo in sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []:
        print(f"- {repo.name}")
        for skill in discover_skills_in_repo(repo, repo.name, "user"):
            desc = f" — {skill.description}" if skill.description else ""
            print(f"  - {skill.name}{desc}")
    return 0


def user_doctor(_args: argparse.Namespace) -> int:
    issues = 0
    paths.ensure_base_dirs()
    print(f"skillhost home: {paths.skillhost_home()}")
    if shutil.which("git"):
        print("git: available")
    else:
        print("git: missing")
        issues += 1
    base = config.user_repos_path_from_config()
    print(f"user_repos: {base}")
    all_skills = []
    for repo in sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []:
        if not is_git_repo(repo):
            print(f"not a git repo: {repo}")
            issues += 1
            continue
        skills = discover_skills_in_repo(repo, repo.name, "user")
        if not skills:
            print(f"no skills found: {repo}")
            issues += 1
        all_skills.extend(skills)
    issues += _report_skill_conflicts(all_skills)
    for name, target in agent_targets("user", None).items():
        print(f"{name} target: {target}")
        issues += _check_target_manifest(target)
    return USER_ERROR if issues else 0


def project_register(args: argparse.Namespace) -> int:
    config.register_project(args.project, args.git)
    print(f"Registered project '{args.project}' for {normalize_git_url(args.git)}")
    return 0


def _require_project_registered(project: str, project_git: str | None = None) -> None:
    if config.get_project(project):
        return
    if project_git:
        config.register_project(project, project_git)
        return
    raise SkillhostError(f"Project '{project}' is not registered. Run project register or pass --project-git.")


def project_add(args: argparse.Namespace) -> int:
    _require_project_registered(args.project, args.project_git)
    base = config.project_repos_path_from_config(args.project)
    base.mkdir(parents=True, exist_ok=True)
    repo_name, dest, exists = _ensure_clone_dest(args.git_repo, base, args.name)
    if exists:
        print(f"Project repo '{repo_name}' already exists at {dest}")
    else:
        clone_repo(args.git_repo, dest, args.branch)
        print(f"Added project repo '{repo_name}' at {dest}")
    return 0


def project_update(args: argparse.Namespace) -> int:
    projects = [args.project] if args.project else sorted(config.list_projects())
    for project in projects:
        _update_repos(config.project_repos_path_from_config(project), args.name)
    return 0


def project_link(args: argparse.Namespace) -> int:
    project, root = current_project_context(args.project)
    skills = discover_repos(config.project_repos_path_from_config(project), "project", project)
    failures = link_skills(
        skills,
        agent_targets("project", args.agent, root),
        "project",
        project=project,
        dry_run=args.dry_run,
    )
    return USER_ERROR if failures else 0


def project_unlink(args: argparse.Namespace) -> int:
    project, root = current_project_context(args.project)
    unlink_scope(
        agent_targets("project", args.agent, root),
        "project",
        project=project,
        dry_run=args.dry_run,
    )
    return 0


def project_remove(args: argparse.Namespace) -> int:
    repo = config.project_repos_path_from_config(args.project) / args.name
    if not repo.exists():
        raise SkillhostError(f"Project repo not found: {args.name}")
    if is_git_repo(repo) and is_dirty(repo) and not args.force:
        raise SkillhostError(f"Repository is dirty; use --force to remove: {repo}")
    try:
        project, root = current_project_context(args.project)
        unlink_scope(agent_targets("project", None, root), "project", project=project, repo_name=args.name)
    except (SkillhostError, GitError):
        print("If project links exist, run 'skillhost project unlink' in the project checkout first.")
    shutil.rmtree(repo)
    print(f"Removed project repo '{args.name}' from project '{args.project}'")
    return 0


def project_list(args: argparse.Namespace) -> int:
    projects = {args.project: config.get_project(args.project)} if args.project else config.list_projects()
    for project, pdata in projects.items():
        if not pdata:
            continue
        print(f"Project: {project}")
        for remote in pdata.get("remotes", []):
            print(f"  remote: {remote}")
        base = config.project_repos_path_from_config(project)
        for repo in sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []:
            print(f"  repo: {repo.name}")
            for skill in discover_skills_in_repo(repo, repo.name, "project", project):
                print(f"    skill: {skill.name}")
    return 0


def project_doctor(args: argparse.Namespace) -> int:
    issues = 0
    projects = [args.project] if args.project else sorted(config.list_projects())
    for project in projects:
        pdata = config.get_project(project)
        if not pdata:
            print(f"missing project: {project}")
            issues += 1
            continue
        print(f"project {project}: remotes={pdata.get('remotes', [])}")
        base = config.project_repos_path_from_config(project)
        all_skills = []
        for repo in sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []:
            if not is_git_repo(repo):
                print(f"not a git repo: {repo}")
                issues += 1
                continue
            skills = discover_skills_in_repo(repo, repo.name, "project", project)
            if not skills:
                print(f"no skills found: {repo}")
                issues += 1
            all_skills.extend(skills)
        issues += _report_skill_conflicts(all_skills)
    try:
        project, root = current_project_context(args.project)
        print(f"current checkout matches project {project}: {root}")
        for name, target in agent_targets("project", None, root).items():
            print(f"{name} target: {target}")
            issues += _check_target_manifest(target)
    except (SkillhostError, GitError) as exc:
        print(f"current checkout: {exc}")
    return USER_ERROR if issues else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillhost")
    parser.add_argument("--version", action="version", version=f"skillhost {__version__}")
    sub = parser.add_subparsers(dest="scope", required=True)

    user = sub.add_parser("user")
    us = user.add_subparsers(dest="command", required=True)

    p = us.add_parser("add")
    p.add_argument("git_repo")
    p.add_argument("--name")
    p.add_argument("--branch")
    p.set_defaults(func=user_add)

    p = us.add_parser("update")
    p.add_argument("name", nargs="?")
    p.set_defaults(func=user_update)

    p = us.add_parser("link")
    p.add_argument("--agent", choices=["codex", "claude", "opencode"])
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=user_link)

    p = us.add_parser("unlink")
    p.add_argument("--agent", choices=["codex", "claude", "opencode"])
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=user_unlink)

    p = us.add_parser("remove")
    p.add_argument("name")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=user_remove)

    us.add_parser("list").set_defaults(func=user_list)
    us.add_parser("doctor").set_defaults(func=user_doctor)

    project = sub.add_parser("project")
    ps = project.add_subparsers(dest="command", required=True)

    p = ps.add_parser("add")
    p.add_argument("git_repo")
    p.add_argument("--project", required=True)
    p.add_argument("--name")
    p.add_argument("--branch")
    p.add_argument("--project-git")
    p.set_defaults(func=project_add)

    p = ps.add_parser("register")
    p.add_argument("project")
    p.add_argument("--git", required=True)
    p.set_defaults(func=project_register)

    p = ps.add_parser("update")
    p.add_argument("project", nargs="?")
    p.add_argument("name", nargs="?")
    p.set_defaults(func=project_update)

    p = ps.add_parser("link")
    p.add_argument("--project")
    p.add_argument("--agent", choices=["codex", "claude", "opencode"])
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=project_link)

    p = ps.add_parser("unlink")
    p.add_argument("--project")
    p.add_argument("--agent", choices=["codex", "claude", "opencode"])
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=project_unlink)

    p = ps.add_parser("remove")
    p.add_argument("name")
    p.add_argument("--project", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=project_remove)

    p = ps.add_parser("list")
    p.add_argument("project", nargs="?")
    p.set_defaults(func=project_list)

    p = ps.add_parser("doctor")
    p.add_argument("project", nargs="?")
    p.set_defaults(func=project_doctor)
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
    except Exception as exc:  # pragma: no cover
        print(f"internal error: {exc}", file=sys.stderr)
        return INTERNAL_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
