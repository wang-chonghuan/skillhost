from __future__ import annotations

import importlib
import subprocess
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
    }


def test_init_creates_json_config(isolated):
    assert main(["init"]) == 0
    assert paths.config_path().name == "config.json"
    cfg = config.load_config()
    assert cfg["version"] == 1
    assert Path(cfg["home"]) == paths.skillhost_home()
    assert "user_repos" in cfg
    assert "projects" in cfg


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
    assert main(["config"]) == 0
    assert capsys.readouterr().out.strip() == str(paths.config_path())


def test_unsupported_old_commands_do_not_exist():
    parser = build_parser()
    subparsers = next(action for action in parser._actions if getattr(action, "dest", None) == "command")
    assert "project" not in subparsers.choices
    assert "user" not in subparsers.choices
    assert "register-project" not in subparsers.choices
