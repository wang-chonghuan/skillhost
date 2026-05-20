from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from skillhost import config
from skillhost.cli import main
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
    reload_agents_for_home(monkeypatch, home)
    return tmp_path


def reload_agents_for_home(monkeypatch, home: Path) -> None:
    import skillhost.agents as agents

    monkeypatch.setattr(
        agents,
        "AGENTS",
        {
            "codex": agents.Agent("codex", home / ".agents" / "skills", Path(".agents") / "skills"),
            "claude": agents.Agent("claude", home / ".claude" / "skills", Path(".claude") / "skills"),
            "opencode": agents.Agent(
                "opencode", home / ".config" / "opencode" / "skills", Path(".opencode") / "skills"
            ),
        },
    )


def make_repo(base: Path, name: str = "repo", skill_name: str = "foo") -> Path:
    repo = base / name
    repo.mkdir()
    git(["init", "-b", "main"], repo)
    skill_dir = repo / skill_name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {skill_name}\ndescription: {skill_name} desc\n---\n", encoding="utf-8"
    )
    git(["add", "."], repo)
    git(["commit", "-m", "init"], repo)
    return repo


def add_remote_commit(repo: Path, skill_name: str = "bar") -> None:
    skill_dir = repo / skill_name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(f"---\nname: {skill_name}\n---\n", encoding="utf-8")
    git(["add", "."], repo)
    git(["commit", "-m", f"add {skill_name}"], repo)


def set_tty(monkeypatch, value: bool) -> None:
    monkeypatch.setattr(sys.stdin, "isatty", lambda: value)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: value)


@pytest.mark.parametrize(
    ("choice", "target_rel"),
    [
        ("1", Path(".agents/skills")),
        ("2", Path(".claude/skills")),
        ("3", Path(".config/opencode/skills")),
    ],
)
def test_interactive_add_builtin_agent_choices(isolated, monkeypatch, choice, target_rel):
    repo = make_repo(isolated, f"repo-{choice}")
    set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _prompt="": choice)

    assert main(["add", str(repo), "--name", f"repo-{choice}"]) == 0

    target = isolated / "home" / target_rel
    assert (target / "foo").is_symlink()
    assert load_manifest(target)["links"]["foo"]["target_kind"] == "agent"


def test_interactive_add_all_supported_agents(isolated, monkeypatch):
    repo = make_repo(isolated, "repo-all")
    set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _prompt="": "4")

    assert main(["add", str(repo), "--name", "repo-all"]) == 0

    for rel in [Path(".agents/skills"), Path(".claude/skills"), Path(".config/opencode/skills")]:
        assert (isolated / "home" / rel / "foo").is_symlink()


def test_interactive_add_custom_directory(isolated, monkeypatch):
    repo = make_repo(isolated, "repo-custom")
    custom = isolated / "custom-skills"
    answers = iter(["5", str(custom)])
    set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    assert main(["add", str(repo), "--name", "repo-custom"]) == 0

    assert (custom / "foo").is_symlink()
    manifest = load_manifest(custom)
    assert manifest["links"]["foo"]["agent"] is None
    assert manifest["links"]["foo"]["target_kind"] == "custom"


def test_interactive_add_skip_default(isolated, monkeypatch):
    repo = make_repo(isolated, "repo-skip")
    set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _prompt="": "")

    assert main(["add", str(repo), "--name", "repo-skip"]) == 0

    assert not (isolated / "home" / ".agents" / "skills" / "foo").exists()


def test_non_interactive_add_does_not_hang_and_suggests_commands(isolated, capsys, monkeypatch):
    repo = make_repo(isolated, "repo-noninteractive")
    set_tty(monkeypatch, False)

    assert main(["add", str(repo), "--name", "repo-noninteractive"]) == 0

    captured = capsys.readouterr()
    assert "To link discovered skills" in captured.out
    assert "skillhost link --agent codex" in captured.out


def test_add_agent_yes_and_target_dir_yes(isolated, monkeypatch):
    repo_agent = make_repo(isolated, "repo-agent", "agent-skill")
    repo_custom = make_repo(isolated, "repo-target", "custom-skill")
    custom = isolated / "target-skills"
    set_tty(monkeypatch, False)

    assert main(["add", str(repo_agent), "--name", "repo-agent", "--agent", "codex", "--yes"]) == 0
    assert main(["add", str(repo_custom), "--name", "repo-target", "--target-dir", str(custom), "--yes"]) == 0

    assert (isolated / "home" / ".agents" / "skills" / "agent-skill").is_symlink()
    assert (custom / "custom-skill").is_symlink()


def test_yes_without_target_fails_clearly(isolated, capsys):
    repo = make_repo(isolated, "repo-yes")

    assert main(["add", str(repo), "--name", "repo-yes", "--yes"]) != 0

    assert "--yes requires --agent or --target-dir" in capsys.readouterr().err


def test_link_target_dir_and_mutual_exclusion(isolated):
    repo = make_repo(isolated, "repo-link")
    custom = isolated / "manual-target"
    assert main(["add", str(repo), "--name", "repo-link", "--no-link-prompt"]) == 0

    assert main(["link", "--target-dir", str(custom)]) == 0
    assert (custom / "foo").is_symlink()
    assert load_manifest(custom)["links"]["foo"]["target_kind"] == "custom"

    with pytest.raises(SystemExit) as excinfo:
        main(["link", "--agent", "codex", "--target-dir", str(custom)])
    assert excinfo.value.code == 2


def test_custom_target_unlink_remove_safe_and_old_manifest_readable(isolated):
    repo = make_repo(isolated, "repo-unlink")
    custom = isolated / "unlink-target"
    assert main(["add", str(repo), "--name", "repo-unlink", "--target-dir", str(custom), "--yes"]) == 0
    (custom / "user-owned").mkdir()

    # Simulate a pre-target_kind manifest from older Skillhost versions.
    manifest = load_manifest(custom)
    manifest["links"]["foo"].pop("target_kind", None)
    (custom / ".skillhost-links.json").write_text(__import__("json").dumps(manifest), encoding="utf-8")

    assert main(["unlink", "--target-dir", str(custom)]) == 0
    assert not (custom / "foo").exists()
    assert (custom / "user-owned").is_dir()


def test_update_defaults_all_and_prompts_to_link_user_and_project(isolated, monkeypatch):
    user_remote = make_repo(isolated, "remote-user", "user-skill")
    project_remote = make_repo(isolated, "remote-project", "project-skill")
    assert main(["add", str(user_remote), "--name", "user-repo", "--no-link-prompt"]) == 0
    assert main(["project", "register", "proj", "--git", "https://example.com/org/proj.git"]) == 0
    assert main(["project", "add", str(project_remote), "--project", "proj", "--name", "project-repo"]) == 0
    add_remote_commit(user_remote, "new-user")
    add_remote_commit(project_remote, "new-project")
    checkout = isolated / "checkout"
    checkout.mkdir()
    git(["init", "-b", "main"], checkout)
    git(["remote", "add", "origin", "https://example.com/org/proj.git"], checkout)
    monkeypatch.chdir(checkout)
    set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _prompt="": "y")

    assert main(["update", "--agent", "codex"]) == 0

    assert (isolated / "home" / ".agents" / "skills" / "new-user").is_symlink()
    assert (checkout / ".agents" / "skills" / "new-project").is_symlink()


def test_update_selectors_user_repo_project_repo_and_all(isolated, monkeypatch):
    repo_one = make_repo(isolated, "remote-one", "one")
    repo_two = make_repo(isolated, "remote-two", "two")
    project_remote = make_repo(isolated, "remote-selector-project", "proj-one")
    assert main(["add", str(repo_one), "--name", "one", "--no-link-prompt"]) == 0
    assert main(["add", str(repo_two), "--name", "two", "--no-link-prompt"]) == 0
    assert main(["project", "register", "proj2", "--git", "https://example.com/org/proj2.git"]) == 0
    assert main(["project", "add", str(project_remote), "--project", "proj2", "--name", "prepo"]) == 0
    add_remote_commit(repo_one, "one-new")
    add_remote_commit(repo_two, "two-new")
    add_remote_commit(project_remote, "proj-new")
    set_tty(monkeypatch, False)

    assert main(["update", "--user_repos", "one", "--agent", "codex", "--yes"]) == 0
    assert (isolated / "home" / ".agents" / "skills" / "one-new").is_symlink()
    assert not (isolated / "home" / ".agents" / "skills" / "two-new").exists()

    assert main(["update", "--project_repos", "proj2/prepo", "--no-link-prompt"]) == 0
    local_project_repo = config.project_repos_path_from_config("proj2") / "prepo"
    assert (local_project_repo / "proj-new" / "SKILL.md").is_file()

    assert main(["update", "--user_repos", "all", "--no-link-prompt"]) == 0
    assert main(["update", "--project_repos", "all", "--no-link-prompt"]) == 0


def test_update_agent_yes_non_interactive_links_without_prompt(isolated, monkeypatch):
    repo = make_repo(isolated, "remote-update-agent", "before")
    assert main(["add", str(repo), "--name", "update-agent", "--no-link-prompt"]) == 0
    add_remote_commit(repo, "after")
    set_tty(monkeypatch, False)

    assert main(["update", "--user_repos", "update-agent", "--agent", "codex", "--yes"]) == 0

    assert (isolated / "home" / ".agents" / "skills" / "after").is_symlink()


def test_interactive_update_yes_prompts_for_target(isolated, monkeypatch):
    repo = make_repo(isolated, "remote-update-yes", "before")
    assert main(["add", str(repo), "--name", "update-yes", "--no-link-prompt"]) == 0
    add_remote_commit(repo, "after")
    answers = iter(["y", "1"])
    set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    assert main(["update"]) == 0

    assert (isolated / "home" / ".agents" / "skills" / "after").is_symlink()


def test_interactive_update_no_does_not_link(isolated, monkeypatch):
    repo = make_repo(isolated, "remote-update-no", "before")
    assert main(["add", str(repo), "--name", "update-no", "--no-link-prompt"]) == 0
    add_remote_commit(repo, "after")
    set_tty(monkeypatch, True)
    monkeypatch.setattr("builtins.input", lambda _prompt="": "n")

    assert main(["update"]) == 0

    assert not (isolated / "home" / ".agents" / "skills" / "after").exists()
