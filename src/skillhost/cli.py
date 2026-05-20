"""Argparse command-line interface for skillhost."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import __version__, config, paths
from .agents import get_agents
from .discovery import Skill, discover_repos, discover_skills_in_repo
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

AGENT_CHOICES = ["codex", "claude", "opencode"]


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


def _is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _custom_targets(target_dir: str | Path) -> dict[str, Path]:
    return {"custom": Path(target_dir).expanduser().resolve()}


def _user_targets(agent: str | None = None, target_dir: str | None = None) -> dict[str, Path]:
    if agent and target_dir:
        raise SkillhostError("Use either --agent or --target-dir, not both.")
    if target_dir:
        return _custom_targets(target_dir)
    return agent_targets("user", agent)


def _target_kinds(targets: dict[str, Path]) -> dict[str, str]:
    return {name: ("agent" if name in AGENT_CHOICES else "custom") for name in targets}


def _link_user_skills(skills: list[Skill], targets: dict[str, Path], dry_run: bool = False) -> int:
    return link_skills(skills, targets, "user", dry_run=dry_run, target_kinds=_target_kinds(targets))


def _print_discovered(skills: list[Skill]) -> None:
    if not skills:
        print("No skills found (no SKILL.md files discovered).")
        return
    noun = "skill" if len(skills) == 1 else "skills"
    print(f"Discovered {len(skills)} {noun}:")
    for skill in skills:
        desc = f" — {skill.description}" if skill.description else ""
        print(f"- {skill.name}{desc}")


def _print_link_suggestions(repo_name: str) -> None:
    print("To link discovered skills, run one of:")
    print("  skillhost link --agent codex")
    print("  skillhost link --agent claude")
    print("  skillhost link --agent opencode")
    print("  skillhost link --target-dir /path/to/skills")
    print(f"Repository '{repo_name}' remains registered for later linking.")


def _prompt_add_link_targets(retry: bool = True) -> dict[str, Path] | None:
    print("Link discovered skills now?")
    print("  1. Codex user skills       ~/.agents/skills")
    print("  2. Claude Code user skills ~/.claude/skills")
    print("  3. OpenCode user skills    ~/.config/opencode/skills")
    print("  4. All supported agents")
    print("  5. Custom directory")
    print("  6. Skip linking")
    while True:
        choice = input("Choose [1-6]: ").strip()
        if choice == "1":
            return agent_targets("user", "codex")
        if choice == "2":
            return agent_targets("user", "claude")
        if choice == "3":
            return agent_targets("user", "opencode")
        if choice == "4":
            return agent_targets("user", None)
        if choice == "5":
            target = input("Custom skill target directory: ").strip()
            if not target:
                print("No custom directory provided; skipping linking.")
                return None
            return _custom_targets(target)
        if choice in {"", "6"}:
            print("Skipping linking.")
            return None
        if not retry:
            raise SkillhostError("Invalid choice. Choose a number from 1 to 6.")
        print("Invalid choice. Choose a number from 1 to 6.")


def _prompt_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        answer = input(prompt + suffix).strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer Y or N.")


def user_add(args: argparse.Namespace) -> int:
    if args.agent and args.target_dir:
        raise SkillhostError("Use either --agent or --target-dir, not both.")
    if args.yes and not args.no_link_prompt and not args.agent and not args.target_dir:
        raise SkillhostError("--yes requires --agent or --target-dir for non-interactive linking.")

    cfg = config.ensure_default_config()
    base = config.user_repos_path_from_config(cfg)
    base.mkdir(parents=True, exist_ok=True)
    repo_name, dest, exists = _ensure_clone_dest(args.git_repo, base, args.name)
    if exists:
        print(f"User repo '{repo_name}' already exists at {dest}")
    else:
        clone_repo(args.git_repo, dest, args.branch)
        print(f"Added user repo '{repo_name}' at {dest}")

    skills = discover_skills_in_repo(dest, repo_name, "user")
    _print_discovered(skills)
    if not skills:
        return 0

    if args.no_link_prompt:
        _print_link_suggestions(repo_name)
        return 0

    if args.agent or args.target_dir:
        targets = _user_targets(args.agent, args.target_dir)
        failures = _link_user_skills(skills, targets)
        return USER_ERROR if failures else 0

    if _is_interactive():
        targets = _prompt_add_link_targets()
        if not targets:
            return 0
        failures = _link_user_skills(skills, targets)
        return USER_ERROR if failures else 0

    _print_link_suggestions(repo_name)
    return 0


def _available_repos(base: Path) -> str:
    if not base.exists():
        return "none"
    names = [repo.name for repo in sorted(p for p in base.iterdir() if p.is_dir())]
    return ", ".join(names) if names else "none"


def _update_repos(base: Path, name: str | None = None) -> list[Path]:
    repos = [base / name] if name else sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []
    updated: list[Path] = []
    for repo in repos:
        if not repo.exists():
            raise SkillhostError(f"Repository not found: {repo}")
        if not is_git_repo(repo):
            raise SkillhostError(f"Not a git repository: {repo}")
        print(f"Updating {repo.name}")
        pull_ff_only(repo)
        updated.append(repo)
    return updated


def _select_user_update_repos(selector: str | None) -> list[Path]:
    base = config.user_repos_path_from_config()
    if selector in {None, "all"}:
        return _update_repos(base)
    if not (base / selector).exists():
        raise SkillhostError(f"User repo not found: {selector}. Available user repos: {_available_repos(base)}")
    return _update_repos(base, selector)


def _project_selector_parts(selector: str) -> tuple[str, str]:
    if "/" not in selector:
        raise SkillhostError("--project_repos must be 'all' or 'PROJECT/REPO'.")
    project, repo = selector.split("/", 1)
    if not project or not repo:
        raise SkillhostError("--project_repos must be 'all' or 'PROJECT/REPO'.")
    return project, repo


def _select_project_update_repos(selector: str | None) -> list[tuple[str, Path]]:
    projects = config.list_projects()
    updated: list[tuple[str, Path]] = []
    if selector in {None, "all"}:
        for project in sorted(projects):
            for repo in _update_repos(config.project_repos_path_from_config(project)):
                updated.append((project, repo))
        return updated

    project, repo_name = _project_selector_parts(selector)
    if project not in projects:
        available = ", ".join(sorted(projects)) if projects else "none"
        raise SkillhostError(f"Project not registered: {project}. Available projects: {available}")
    base = config.project_repos_path_from_config(project)
    if not (base / repo_name).exists():
        raise SkillhostError(
            f"Project repo not found: {project}/{repo_name}. Available repos for {project}: {_available_repos(base)}"
        )
    for repo in _update_repos(base, repo_name):
        updated.append((project, repo))
    return updated


def _discover_user_repos_by_path(repos: list[Path]) -> list[Skill]:
    skills: list[Skill] = []
    for repo in repos:
        skills.extend(discover_skills_in_repo(repo, repo.name, "user"))
    return skills


def _discover_project_repos_by_path(repos: list[tuple[str, Path]]) -> list[Skill]:
    skills: list[Skill] = []
    for project, repo in repos:
        skills.extend(discover_skills_in_repo(repo, repo.name, "project", project))
    return skills


def _link_updated_project_skills(
    project_repos: list[tuple[str, Path]], agent: str | None, dry_run: bool = False
) -> int:
    failures = 0
    by_project: dict[str, list[Path]] = {}
    for project, repo in project_repos:
        by_project.setdefault(project, []).append(repo)
    for project, repos in by_project.items():
        try:
            resolved_project, root = current_project_context(project)
        except (SkillhostError, GitError) as exc:
            print(f"Skipping project links for '{project}': {exc}", file=sys.stderr)
            failures += 1
            continue
        skills = _discover_project_repos_by_path([(resolved_project, repo) for repo in repos])
        failures += link_skills(
            skills,
            agent_targets("project", agent, root),
            "project",
            project=resolved_project,
            dry_run=dry_run,
        )
    return failures


def _maybe_link_updated(args: argparse.Namespace, user_repos: list[Path], project_repos: list[tuple[str, Path]]) -> int:
    if not user_repos and not project_repos:
        print("No repositories configured.")
        return 0

    if args.no_link_prompt:
        print("Updated repositories. Run 'skillhost link' to refresh user-level links.")
        return 0

    direct_target = bool(args.agent or args.target_dir)
    if _is_interactive() and not args.yes:
        if not _prompt_yes_no("Link updated skills now?", default=True):
            return 0
        if not direct_target:
            targets = _prompt_add_link_targets() if user_repos else None
            if user_repos and not targets:
                return 0
            args._prompt_targets = targets
    elif not direct_target:
        print("Updated repositories. Run 'skillhost link' to refresh user-level links.")
        return 0

    failures = 0
    user_skills = _discover_user_repos_by_path(user_repos)
    if user_skills:
        targets = getattr(args, "_prompt_targets", None) or _user_targets(args.agent, args.target_dir)
        failures += _link_user_skills(user_skills, targets)
    if project_repos:
        if args.target_dir:
            print("Skipping project repo links for --target-dir; custom targets are user-level only.", file=sys.stderr)
        else:
            failures += _link_updated_project_skills(project_repos, args.agent)
    return USER_ERROR if failures else 0


def user_update(args: argparse.Namespace) -> int:
    if args.agent and args.target_dir:
        raise SkillhostError("Use either --agent or --target-dir, not both.")
    if args.yes and not args.no_link_prompt and not args.agent and not args.target_dir:
        raise SkillhostError("--yes requires --agent or --target-dir for non-interactive linking.")

    user_selector = args.user_repos
    if getattr(args, "name", None) and user_selector is None:
        user_selector = args.name

    update_user = user_selector is not None or args.project_repos is None
    update_project = args.project_repos is not None or user_selector is None

    user_repos = _select_user_update_repos(user_selector) if update_user else []
    project_repos = _select_project_update_repos(args.project_repos) if update_project else []
    return _maybe_link_updated(args, user_repos, project_repos)


def user_link(args: argparse.Namespace) -> int:
    skills = discover_repos(config.user_repos_path_from_config(), "user")
    targets = _user_targets(args.agent, args.target_dir)
    failures = _link_user_skills(skills, targets, dry_run=args.dry_run)
    return USER_ERROR if failures else 0


def user_unlink(args: argparse.Namespace) -> int:
    targets = _user_targets(args.agent, args.target_dir)
    unlink_scope(targets, "user", dry_run=args.dry_run)
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
        if pdata is None:
            raise SkillhostError(f"Project not registered: {project}")
        print(f"Project: {project}")
        base = config.project_repos_path_from_config(project)
        repos = sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []
        for repo in repos:
            print(f"- {repo.name}")
            for skill in discover_skills_in_repo(repo, repo.name, "project", project):
                desc = f" — {skill.description}" if skill.description else ""
                print(f"  - {skill.name}{desc}")
    return 0


def project_doctor(args: argparse.Namespace) -> int:
    issues = 0
    projects = [args.project] if args.project else sorted(config.list_projects())
    for project in projects:
        print(f"Project: {project}")
        base = config.project_repos_path_from_config(project)
        print(f"project_repos: {base}")
        skills = discover_repos(base, "project", project)
        issues += _report_skill_conflicts(skills)
    try:
        project, root = current_project_context(args.project)
        for name, target in agent_targets("project", None, root).items():
            print(f"{name} target: {target}")
            issues += _check_target_manifest(target)
    except (SkillhostError, GitError) as exc:
        print(f"current checkout: {exc}")
    return USER_ERROR if issues else 0


def _add_target_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--agent", choices=AGENT_CHOICES)
    group.add_argument("--target-dir")


def _add_user_commands(sub: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p = sub.add_parser("add")
    p.add_argument("git_repo")
    p.add_argument("--name")
    p.add_argument("--branch")
    _add_target_args(p)
    p.add_argument("--no-link-prompt", action="store_true", help="Do not ask where to link discovered skills")
    p.add_argument(
        "--yes",
        action="store_true",
        help="Confirm non-interactive linking when used with --agent or --target-dir",
    )
    p.set_defaults(func=user_add)

    p = sub.add_parser("update")
    p.add_argument("name", nargs="?", help=argparse.SUPPRESS)
    p.add_argument("--user_repos", "--user-repos", dest="user_repos")
    p.add_argument("--project_repos", "--project-repos", dest="project_repos")
    _add_target_args(p)
    p.add_argument(
        "--yes",
        action="store_true",
        help="Confirm non-interactive linking when used with --agent or --target-dir",
    )
    p.add_argument("--no-link-prompt", action="store_true", help="Do not ask whether to link after updating")
    p.set_defaults(func=user_update)

    p = sub.add_parser("link")
    _add_target_args(p)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=user_link)

    p = sub.add_parser("unlink")
    _add_target_args(p)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=user_unlink)

    p = sub.add_parser("remove")
    p.add_argument("name")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=user_remove)

    sub.add_parser("list").set_defaults(func=user_list)
    sub.add_parser("doctor").set_defaults(func=user_doctor)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillhost")
    parser.add_argument("--version", action="version", version=f"skillhost {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    _add_user_commands(sub)

    project = sub.add_parser("project")
    ps = project.add_subparsers(dest="project_command", required=True)

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
    p.add_argument("--agent", choices=AGENT_CHOICES)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=project_link)

    p = ps.add_parser("unlink")
    p.add_argument("--project")
    p.add_argument("--agent", choices=AGENT_CHOICES)
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
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        return USER_ERROR
    except Exception as exc:  # pragma: no cover
        print(f"internal error: {exc}", file=sys.stderr)
        return INTERNAL_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
