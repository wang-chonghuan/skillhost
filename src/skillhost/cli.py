from __future__ import annotations

import argparse
import os
import subprocess
import shutil
import sys
import tempfile
import termios
import tty
from pathlib import Path

from . import __version__, config, paths
from .discovery import Skill, discover_repos
from .errors import GIT_ERROR, INTERNAL_ERROR, USER_ERROR, GitError, SkillhostError
from .git_utils import clone_repo, derive_repo_name, get_repo_root, is_git_repo, pull_ff_only
from .linking import MANIFEST, link_skills, load_manifest, save_manifest, unlink_scope
from .projects import current_project_context

AGENT_CHOICES = ["codex", "claude", "opencode", "openclaw", "hermes"]


def _is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _format_agent_label(agent_name: str) -> str:
    labels = {
        "codex": "Codex",
        "claude": "Claude Code",
        "opencode": "OpenCode",
        "openclaw": "OpenClaw",
        "hermes": "Hermes Agent",
    }
    return labels.get(agent_name, agent_name)


def _parse_add_agent_choice(value: str) -> list[str] | None:
    value = value.strip().lower()
    if not value:
        return None
    all_tokens = {"all", "a", str(len(AGENT_CHOICES) + 1)}
    tokens = [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]
    if not tokens or any(token in all_tokens for token in tokens):
        return None

    selected: list[str] = []
    for token in tokens:
        if token.isdigit():
            index = int(token)
            if 1 <= index <= len(AGENT_CHOICES):
                agent_name = AGENT_CHOICES[index - 1]
            else:
                raise SkillhostError(f"Invalid add target choice: {token}")
        else:
            aliases = {
                "claude-code": "claude",
                "claudecode": "claude",
                "open-code": "opencode",
                "hermes-agent": "hermes",
                "hermesagent": "hermes",
            }
            agent_name = aliases.get(token, token)
            if agent_name not in AGENT_CHOICES:
                raise SkillhostError(f"Invalid add target choice: {token}")
        if agent_name not in selected:
            selected.append(agent_name)
    return selected


def _prompt_add_agents_text() -> list[str] | None:
    print("Link added skills to:")
    for index, agent_name in enumerate(AGENT_CHOICES, start=1):
        print(f"  {index}. {_format_agent_label(agent_name)}")
    print(f"  {len(AGENT_CHOICES) + 1}. All")
    try:
        value = input("Choose targets (comma-separated, default All): ")
    except (EOFError, OSError):
        return None
    return _parse_add_agent_choice(value)


def _prompt_add_agents_tui() -> list[str] | None:
    options = [*AGENT_CHOICES, "all"]
    cursor = 0
    selected: set[str] = set()
    line_count = 0

    def checked(option: str) -> bool:
        if option == "all":
            return len(selected) == len(AGENT_CHOICES)
        return option in selected

    def render() -> None:
        nonlocal line_count
        if line_count:
            sys.stdout.write(f"\x1b[{line_count}A")
        lines = ["\x1b[1;36mLink added skills to:\x1b[0m"]
        for index, option in enumerate(options):
            active = index == cursor
            pointer = "❯" if active else " "
            mark = "◉" if checked(option) else "○"
            label = "All" if option == "all" else _format_agent_label(option)
            color = "\x1b[1;32m" if active else "\x1b[37m"
            lines.append(f"{color}{pointer} {mark} {label}\x1b[0m")
        lines.append("\x1b[2m↑/↓ move · Space select · Enter confirm (none = All)\x1b[0m")
        for line in lines:
            sys.stdout.write("\r\x1b[2K" + line + "\r\n")
        sys.stdout.flush()
        line_count = len(lines)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdout.write("\x1b[?25l")
        while True:
            render()
            char = sys.stdin.read(1)
            if char == "\x03":
                raise KeyboardInterrupt
            if char in {"\r", "\n"}:
                break
            if char == " ":
                option = options[cursor]
                if option == "all":
                    if len(selected) == len(AGENT_CHOICES):
                        selected.clear()
                    else:
                        selected = set(AGENT_CHOICES)
                elif option in selected:
                    selected.remove(option)
                else:
                    selected.add(option)
            elif char == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":
                    cursor = (cursor - 1) % len(options)
                elif seq == "[B":
                    cursor = (cursor + 1) % len(options)
        sys.stdout.write("\r\x1b[?25h")
        sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        sys.stdout.write("\r\x1b[?25h")
        sys.stdout.flush()

    if not selected or len(selected) == len(AGENT_CHOICES):
        return None
    return [agent for agent in AGENT_CHOICES if agent in selected]


def _prompt_add_agents() -> list[str] | None:
    if not _is_interactive():
        return _prompt_add_agents_text()
    try:
        return _prompt_add_agents_tui()
    except (termios.error, OSError):
        return _prompt_add_agents_text()


def _select_add_targets() -> list[str] | None:
    return _prompt_add_agents()


def _relink_add_targets(scope: str, project: str | None, repo_name: str, agent_names: list[str] | None) -> int:
    if agent_names is None:
        return _relink_selected(scope, project, repo_name, None)
    failures = 0
    for agent_name in agent_names:
        failures |= _relink_selected(scope, project, repo_name, agent_name)
    return USER_ERROR if failures else 0


def _print_add_summary(skill_count: int) -> None:
    label = "skill" if skill_count == 1 else "skills"
    print(f"{skill_count} {label} added.")
    print("Run `skillhost list` to view installed skills.")


def _unlink_repo_links(scope: str, project: str | None, repo_name: str, agent_name: str | None) -> int:
    removed = 0
    for target_agent_name, target in _target_entries(scope, project, agent_name):
        removed += unlink_scope({target_agent_name: target}, scope, project=project, repo_name=repo_name)
    return removed


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


def _repo_name_arg(value: str | None, command: str) -> str:
    raw = _require_repo_name(value, command)
    if "://" in raw or raw.startswith("git@") or raw.endswith(".git"):
        return derive_repo_name(raw)
    return raw


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

    base_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{repo_name}-", dir=base_dir) as tmp:
        tmp_dest = Path(tmp) / repo_name
        clone_repo(args.skill_git_repo, tmp_dest)
        skills = discover_repos(Path(tmp), scope, project)
        if not skills:
            raise SkillhostError("No skills found in repo; nothing was added.")
        agent_names = _select_add_targets()
        shutil.move(str(tmp_dest), dest)

    config.register_repo(scope, repo_name, args.skill_git_repo, dest, project)
    print(f"Added repo '{repo_name}'.")
    if scope == "user":
        code = _relink_add_targets(scope, project, repo_name, agent_names)
        _print_add_summary(len(skills))
        return code
    try:
        code = _relink_add_targets(scope, project, repo_name, agent_names)
        _print_add_summary(len(skills))
        return code
    except SkillhostError:
        print(f"Added project skill repo for {project}.")
        print("Run inside the project checkout:")
        print(f"  skillhost relink --project {project}")
        _print_add_summary(len(skills))
        return 0


def _selected_agent_names(agent_name: str | None) -> list[str] | None:
    if agent_name:
        return [agent_name]
    return _select_add_targets()


def _unlink_repo_links_for_agents(
    scope: str,
    project: str | None,
    repo_name: str,
    agent_names: list[str] | None,
) -> int:
    if agent_names is None:
        return _unlink_repo_links(scope, project, repo_name, None)
    removed = 0
    for agent_name in agent_names:
        removed += _unlink_repo_links(scope, project, repo_name, agent_name)
    return removed


def _relink_selected_agents(
    scope: str,
    project: str | None,
    repo_name: str | None,
    agent_names: list[str] | None,
) -> int:
    if agent_names is None:
        return _relink_selected(scope, project, repo_name, None)
    failures = 0
    for agent_name in agent_names:
        failures |= _relink_selected(scope, project, repo_name, agent_name)
    return USER_ERROR if failures else 0


def cmd_update(args: argparse.Namespace) -> int:
    scope, base_dir, project = _selected_scope(args.project)
    names = _all_repo_names(scope, project)
    if args.repo_name:
        if args.repo_name not in names:
            raise SkillhostError(f"Repo not found in selected scope: {args.repo_name}")
        names = [args.repo_name]
    agent_names = _selected_agent_names(args.agent)
    if scope == "user":
        for name in names:
            _unlink_repo_links_for_agents(scope, project, name, agent_names)
            pull_ff_only(base_dir / name)
            print(f"Updated {name}")
        return _relink_selected_agents(scope, project, args.repo_name, agent_names)

    can_relink = True
    try:
        for name in names:
            _unlink_repo_links_for_agents(scope, project, name, agent_names)
    except SkillhostError:
        can_relink = False
    for name in names:
        pull_ff_only(base_dir / name)
        print(f"Updated {name}")
    if can_relink:
        try:
            return _relink_selected_agents(scope, project, args.repo_name, agent_names)
        except SkillhostError:
            pass
    print("Updated project skill repo(s).")
    print("Run inside the project checkout:")
    print(f"  skillhost relink --project {project}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    scope, base_dir, project = _selected_scope(args.project)
    name = _repo_name_arg(args.repo_name, "remove")
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
    if args.agent:
        return _relink_selected(scope, project, args.repo_name, args.agent)
    agent_names = _select_add_targets()
    if agent_names is None:
        return _relink_selected(scope, project, args.repo_name, None)
    failures = 0
    for agent_name in agent_names:
        failures |= _relink_selected(scope, project, args.repo_name, agent_name)
    return USER_ERROR if failures else 0


def cmd_unlink(args: argparse.Namespace) -> int:
    scope, _base_dir, project = _selected_scope(args.project)
    if not args.repo_name and not args.all:
        raise SkillhostError("Refusing to unlink all links implicitly. Use --all.")
    removed = 0
    for agent_name, target in _target_entries(scope, project, args.agent):
        removed += unlink_scope({agent_name: target}, scope, project=project, repo_name=args.repo_name)
    print(f"Unlinked {removed} skill(s).")
    return 0


def _clean_target(agent_name: str, target: Path, scope: str) -> tuple[int, int]:
    removed = 0
    stale_records = 0
    if not target.exists():
        return removed, stale_records

    manifest = load_manifest(target)
    changed = False

    for child in target.iterdir():
        if child.is_symlink() and not child.exists():
            label = f"{agent_name}:{child.name}" if scope == "user" else f"project:{agent_name}:{child.name}"
            print(f"Remove broken symlink {label}")
            child.unlink()
            removed += 1
            if child.name in manifest.get("links", {}):
                manifest["links"].pop(child.name, None)
                changed = True

    for name, record in list(manifest.get("links", {}).items()):
        if record.get("scope") != scope:
            continue
        dest = target / name
        source = record.get("source")
        if not dest.exists() and not dest.is_symlink():
            label = f"{agent_name}:{name}" if scope == "user" else f"project:{agent_name}:{name}"
            print(f"Remove stale manifest entry {label}")
            manifest["links"].pop(name, None)
            stale_records += 1
            changed = True
        elif dest.is_symlink() and source and not Path(source).exists():
            label = f"{agent_name}:{name}" if scope == "user" else f"project:{agent_name}:{name}"
            print(f"Remove broken symlink {label}")
            dest.unlink()
            manifest["links"].pop(name, None)
            removed += 1
            changed = True

    if changed:
        save_manifest(target, manifest)
    return removed, stale_records


def _project_clean_targets() -> list[tuple[str, Path, str]]:
    if not is_git_repo(Path.cwd()):
        return []
    root = get_repo_root(Path.cwd())
    targets: list[tuple[str, Path, str]] = []
    for name, data in config.get_registered_agents().items():
        if not data.get("enabled", True):
            continue
        project_dir = data.get("project_dir")
        if project_dir:
            targets.append((name, root / project_dir, "project"))
    return targets


def cmd_clean(_args: argparse.Namespace) -> int:
    removed = 0
    stale_records = 0
    clean_targets = [(agent_name, target, "user") for agent_name, target in _target_entries("user", None, None)]
    clean_targets.extend(_project_clean_targets())
    for agent_name, target, scope in clean_targets:
        target_removed, target_stale = _clean_target(agent_name, target, scope)
        removed += target_removed
        stale_records += target_stale
    print(f"Cleaned {removed} broken symlink(s) and {stale_records} stale manifest entrie(s).")
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


def _upgrade_command() -> list[str]:
    executable = Path(sys.executable).resolve()
    executable_parts = set(executable.parts)
    env = os.environ

    if "pipx" in executable_parts or env.get("PIPX_HOME"):
        return ["pipx", "upgrade", "skillhost"]

    uv_tool_dir = env.get("UV_TOOL_DIR")
    if uv_tool_dir and executable.is_relative_to(Path(uv_tool_dir).expanduser().resolve()):
        return ["uv", "tool", "upgrade", "skillhost"]

    if "uv" in executable_parts and "tools" in executable_parts:
        return ["uv", "tool", "upgrade", "skillhost"]

    return [sys.executable, "-m", "pip", "install", "--upgrade", "skillhost"]


def cmd_upgrade(_args: argparse.Namespace) -> int:
    command = _upgrade_command()
    print("Upgrading SkillHost with:")
    print("  " + " ".join(command))
    result = subprocess.run(command)
    if result.returncode == 0:
        print("SkillHost upgraded.")
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillhost")
    parser.add_argument("--version", action="version", version=f"skillhost {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("upgrade").set_defaults(func=cmd_upgrade)

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

    sub.add_parser("clean").set_defaults(func=cmd_clean)

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
