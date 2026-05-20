from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from skillhost import config, paths
from skillhost.cli import build_parser, main
from skillhost.linking import load_manifest


def git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        check=True,
        capture_output=True,
        env={
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    home = tmp_path / "home"
    skillhost_home = tmp_path / "skillhost-home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("SKILLHOST_HOME", str(skillhost_home))
    import skillhost.config as config_module
    importlib.reload(config_module)
    return tmp_path


def fixture_repo_url(repo_name: str) -> str:
    fixture_path = Path(__file__).with_name("fixture_repos.json")
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    return data["skill_repos"][repo_name]


def make_repo(base: Path, name: str = "repo", skill_name: str = "foo") -> Path:
    repo = base / name
    repo.mkdir()
    git(["init", "-b", "main"], repo)
    skill_dir = repo / skill_name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(f"---\nname: {skill_name}\n---\n", encoding="utf-8")
    git(["add", "."], repo)
    git(["commit", "-m", "init"], repo)
    return repo


def test_help_surface_matches_v7():
    parser = build_parser()
    subparsers = next(action for action in parser._actions if getattr(action, "dest", None) == "command")
    command_names = set(subparsers.choices)
    assert command_names == {
        "init",
        "register",
        "unregister",
        "add",
        "update",
        "remove",
        "relink",
        "unlink",
        "list",
        "projects",
        "agents",
        "doctor",
        "config",
        "clean",
    }


def test_init_creates_json_config(isolated, capsys):
    assert main(["init"]) == 0
    assert paths.config_path().name == "config.json"
    cfg = config.load_config()
    assert cfg["version"] == 1
    assert Path(cfg["home"]) == paths.skillhost_home()
    assert "user_repos" in cfg
    assert "projects" in cfg
    assert cfg["agents"]["openclaw"]["user_dir"].endswith(".openclaw/skills")
    assert cfg["agents"]["openclaw"]["project_dir"] == ""
    assert cfg["agents"]["hermes"]["user_dir"].endswith(".hermes/skills")
    assert cfg["agents"]["hermes"]["project_dir"] == ""
    out = capsys.readouterr().out
    assert "SkillHost initialized." in out
    assert f"Home: {paths.skillhost_home()}" in out
    assert f"Config: {paths.config_path()}" in out
    assert "skillhost add <skill-git-repo>" in out


def test_register_and_unregister_project(isolated):
    assert main(["register", "--project", "nsdk", "--git", "git@github.com:org/nsdk.git"]) == 0
    cfg = config.load_config()
    assert cfg["projects"]["nsdk"]["remotes"] == ["github.com/org/nsdk"]
    assert main(["unregister", "--project", "nsdk"]) == 0
    assert "nsdk" not in config.load_config()["projects"]


def test_register_agent_requires_target_dir(isolated):
    assert main(["register", "--agent", "cursor"]) == 1


def test_register_and_unregister_agent(isolated):
    user_dir = isolated / "cursor-skills"
    assert main(["register", "--agent", "cursor", "--user-dir", str(user_dir), "--project-dir", ".cursor/skills"]) == 0
    cfg = config.load_config()
    assert cfg["agents"]["cursor"]["user_dir"] == str(user_dir.resolve())
    assert main(["unregister", "--agent", "cursor"]) == 0
    assert "cursor" not in config.load_config()["agents"]


def test_add_list_relink_unlink_remove_user_scope(isolated):
    repo = make_repo(isolated, "repo-user", "alpha")
    assert main(["add", str(repo), "--name", "repo-user"]) == 0
    cfg = config.load_config()
    assert cfg["user_repos"]["repo-user"]["path"].endswith("user_repos/repo-user")

    target = isolated / "home" / ".agents" / "skills"
    assert (target / "alpha").is_symlink()
    manifest = load_manifest(target)
    assert manifest["links"]["alpha"]["repo"] == "repo-user"

    assert main(["unlink", "repo-user", "--agent", "codex"]) == 0
    assert not (target / "alpha").exists()

    assert main(["remove", "repo-user"]) == 0
    assert "repo-user" not in config.load_config()["user_repos"]




def test_remove_accepts_git_url_as_repo_name(isolated):
    repo = make_repo(isolated, "url-repo", "url-skill")
    assert main(["add", str(repo), "--name", "skill-collection-study"]) == 0

    assert main(["remove", fixture_repo_url("skill-collection-study")]) == 0

    assert "skill-collection-study" not in config.load_config()["user_repos"]
    assert not (paths.user_repos_dir() / "skill-collection-study").exists()




def test_add_cancel_during_target_prompt_leaves_no_state(isolated, monkeypatch):
    repo = make_repo(isolated, "repo-cancel", "cancel-skill")
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    def cancel():
        raise KeyboardInterrupt

    monkeypatch.setattr("skillhost.cli._prompt_add_agents_tui", cancel)

    assert main(["add", str(repo), "--name", "repo-cancel"]) == 1

    assert "repo-cancel" not in config.load_config()["user_repos"]
    assert not (paths.user_repos_dir() / "repo-cancel").exists()
    assert not list(paths.user_repos_dir().glob(".repo-cancel-*"))


def test_add_repo_with_no_skills_leaves_no_state(isolated, capsys):
    repo = isolated / "empty-repo"
    repo.mkdir()
    git(["init", "-b", "main"], repo)
    (repo / "README.md").write_text("# Empty\n", encoding="utf-8")
    git(["add", "."], repo)
    git(["commit", "-m", "init"], repo)

    assert main(["add", str(repo), "--name", "empty-repo"]) == 1

    cfg = config.load_config()
    assert "empty-repo" not in cfg["user_repos"]
    assert not (paths.user_repos_dir() / "empty-repo").exists()
    assert not list(paths.user_repos_dir().glob(".empty-repo-*"))
    assert "No skills found in repo; nothing was added." in capsys.readouterr().err


def test_add_prints_skill_count_and_list_hint(isolated, capsys):
    repo = make_repo(isolated, "repo-count", "counted")

    assert main(["add", str(repo), "--name", "repo-count"]) == 0

    out = capsys.readouterr().out
    assert "1 skill added." in out
    assert "Run `skillhost list` to view installed skills." in out


def test_clean_removes_user_level_broken_symlinks_and_manifest_records(isolated, capsys):
    repo = make_repo(isolated, "repo-clean", "to-clean")
    assert main(["add", str(repo), "--name", "repo-clean"]) == 0
    target = isolated / "home" / ".agents" / "skills"
    link = target / "to-clean"
    assert link.is_symlink()

    shutil.rmtree(paths.user_repos_dir() / "repo-clean")

    assert main(["clean"]) == 0

    assert not link.exists()
    assert not link.is_symlink()
    manifest = load_manifest(target)
    assert "to-clean" not in manifest["links"]
    out = capsys.readouterr().out
    assert "Remove broken symlink codex:to-clean" in out
    assert "Cleaned 5 broken symlink(s)" in out


def test_clean_also_removes_current_repo_project_level_broken_symlinks(isolated, monkeypatch, capsys):
    project = make_repo(isolated, "repo-project-clean", "project-source")
    monkeypatch.chdir(project)
    target = project / ".agents" / "skills"
    source = project / "missing-project-skill"
    target.mkdir(parents=True)
    (target / "broken-project").symlink_to(source, target_is_directory=True)

    assert main(["clean"]) == 0

    assert not (target / "broken-project").exists()
    assert not (target / "broken-project").is_symlink()
    out = capsys.readouterr().out
    assert "Remove broken symlink project:codex:broken-project" in out
    assert "Cleaned 1 broken symlink(s)" in out


def test_clean_skips_user_only_agents_for_project_level(isolated, monkeypatch):
    project = make_repo(isolated, "repo-project-user-only-clean", "project-source")
    monkeypatch.chdir(project)
    hermes_target = project / ".hermes" / "skills"
    hermes_target.mkdir(parents=True)
    (hermes_target / "broken-hermes-project").symlink_to(project / "missing", target_is_directory=True)

    assert main(["clean"]) == 0

    assert (hermes_target / "broken-hermes-project").is_symlink()

def test_update_unlinks_old_skill_names_before_relinking(isolated):
    repo = make_repo(isolated, "repo-rename", "old-skill")
    assert main(["add", str(repo), "--name", "repo-rename"]) == 0
    target = isolated / "home" / ".agents" / "skills"
    assert (target / "old-skill").is_symlink()

    git(["mv", "old-skill", "new-skill"], repo)
    (repo / "new-skill" / "SKILL.md").write_text("---\nname: new-skill\n---\n", encoding="utf-8")
    git(["add", "."], repo)
    git(["commit", "-m", "rename skill"], repo)

    assert main(["update", "repo-rename"]) == 0

    assert not (target / "old-skill").exists()
    assert not (target / "old-skill").is_symlink()
    assert (target / "new-skill").is_symlink()
    manifest = load_manifest(target)
    assert "old-skill" not in manifest["links"]
    assert manifest["links"]["new-skill"]["repo"] == "repo-rename"


def test_add_interactive_links_selected_agents(isolated, monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _prompt: "1,3")
    repo = make_repo(isolated, "repo-selected", "selected")

    assert main(["add", str(repo), "--name", "repo-selected"]) == 0

    codex_target = isolated / "home" / ".agents" / "skills"
    claude_target = isolated / "home" / ".claude" / "skills"
    opencode_target = isolated / "home" / ".config" / "opencode" / "skills"
    assert (codex_target / "selected").is_symlink()
    assert not (claude_target / "selected").exists()
    assert (opencode_target / "selected").is_symlink()


def test_add_interactive_all_choice_links_all_agents(isolated, monkeypatch):
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _prompt: "all")
    repo = make_repo(isolated, "repo-all", "allskill")

    assert main(["add", str(repo), "--name", "repo-all"]) == 0

    assert (isolated / "home" / ".agents" / "skills" / "allskill").is_symlink()
    assert (isolated / "home" / ".claude" / "skills" / "allskill").is_symlink()
    assert (isolated / "home" / ".config" / "opencode" / "skills" / "allskill").is_symlink()
    assert (isolated / "home" / ".openclaw" / "skills" / "allskill").is_symlink()
    assert (isolated / "home" / ".hermes" / "skills" / "allskill").is_symlink()


def test_relink_interactive_uses_add_target_selector(isolated, monkeypatch):
    repo = make_repo(isolated, "repo-relink-selected", "relinked")
    assert main(["add", str(repo), "--name", "repo-relink-selected"]) == 0
    assert main(["unlink", "repo-relink-selected", "--agent", "claude"]) == 0
    assert not (isolated / "home" / ".claude" / "skills" / "relinked").exists()

    from skillhost.cli import _prompt_add_agents_text

    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _prompt: "2")
    monkeypatch.setattr("skillhost.cli._prompt_add_agents_tui", lambda: _prompt_add_agents_text())

    assert main(["relink", "repo-relink-selected"]) == 0

    assert (isolated / "home" / ".claude" / "skills" / "relinked").is_symlink()


def test_relink_openclaw_and_hermes_user_agents(isolated):
    repo = make_repo(isolated, "repo-new-agents", "newagent")
    assert main(["add", str(repo), "--name", "repo-new-agents"]) == 0

    assert (isolated / "home" / ".openclaw" / "skills" / "newagent").is_symlink()
    assert (isolated / "home" / ".hermes" / "skills" / "newagent").is_symlink()


def test_project_relink_skips_user_only_agents(isolated, monkeypatch):
    project_repo = make_repo(isolated, "project-user-only", "project-skill")
    skill_repo = make_repo(isolated, "project-user-only-skills", "helper")
    assert main(["register", "--project", "proj-user-only", "--git", str(project_repo)]) == 0
    monkeypatch.chdir(project_repo)

    assert main(["add", str(skill_repo), "--project", "proj-user-only", "--name", "proj-skills"]) == 0

    assert not (project_repo / ".openclaw" / "skills" / "helper").exists()
    assert not (project_repo / ".hermes" / "skills" / "helper").exists()


def test_project_add_writes_nested_project_repos(isolated, monkeypatch, capsys):
    project_repo = make_repo(isolated, "nsdk", "project-skill")
    skill_repo = make_repo(isolated, "nsdk-skills", "helper")
    assert main(["register", "--project", "nsdk", "--git", str(project_repo)]) == 0
    monkeypatch.chdir(isolated)

    assert main(["add", str(skill_repo), "--project", "nsdk", "--name", "nsdk-skills"]) == 0
    cfg = config.load_config()
    assert cfg["projects"]["nsdk"]["repos"]["nsdk-skills"]["path"].endswith("project_repos/nsdk/nsdk-skills")
    out = capsys.readouterr().out
    assert "Run inside the project checkout:" in out


def test_project_relink_validates_current_git_project(isolated, monkeypatch, capsys):
    project_repo = make_repo(isolated, "nsdk", "project-skill")
    skill_repo = make_repo(isolated, "nsdk-skills", "helper")
    assert main(["register", "--project", "nsdk", "--git", str(project_repo)]) == 0
    assert main(["add", str(skill_repo), "--project", "nsdk", "--name", "nsdk-skills"]) == 0
    monkeypatch.chdir(isolated)
    code = main(["relink", "--project", "nsdk"])
    assert code != 0
    assert "not a git repository" in capsys.readouterr().err


def test_unlink_requires_explicit_all(isolated, capsys):
    assert main(["init"]) == 0
    code = main(["unlink"])
    assert code == 1
    assert "Refusing to unlink all links implicitly. Use --all." in capsys.readouterr().err


def test_config_prints_absolute_path(isolated, capsys):
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["config"]) == 0
    assert capsys.readouterr().out.strip() == str(paths.config_path())


def test_unsupported_old_commands_do_not_exist():
    parser = build_parser()
    subparsers = next(action for action in parser._actions if getattr(action, "dest", None) == "command")
    assert "project" not in subparsers.choices
    assert "user" not in subparsers.choices
    assert "register-project" not in subparsers.choices
