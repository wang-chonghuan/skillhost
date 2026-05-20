from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest




def load_fixture_config() -> dict:
    config_path = Path(__file__).with_name("fixture_repos.json")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data["expected_skills"] = {name: set(skills) for name, skills in data["expected_skills"].items()}
    return data


FIXTURES = load_fixture_config()
PROJECT_REPOS = FIXTURES["project_repos"]
SKILL_REPOS = FIXTURES["skill_repos"]
EXPECTED_SKILLS = FIXTURES["expected_skills"]
PROJECT_SKILL_REPO = FIXTURES["project_skill_repo"]

USER_AGENT_DIRS = {
    "codex": Path.home() / ".agents" / "skills",
    "claude": Path.home() / ".claude" / "skills",
    "opencode": Path.home() / ".config" / "opencode" / "skills",
    "openclaw": Path.home() / ".openclaw" / "skills",
    "hermes": Path.home() / ".hermes" / "skills",
}
PROJECT_AGENT_DIRS = {
    "codex": Path(".agents") / "skills",
    "claude": Path(".claude") / "skills",
    "opencode": Path(".opencode") / "skills",
}
REAL_CHECKOUT_ROOT = Path.home() / ".skillhost" / "real_e2e_checkouts"


def run_cmd(args: list[str], *, cwd: Path | None = None, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("SKILLHOST_HOME", None)
    env["HOME"] = str(Path.home())
    result = subprocess.run(args, cwd=cwd, input=input_text, text=True, capture_output=True, env=env)
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed with {result.returncode}: {' '.join(args)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def run_skillhost(args: list[str], *, cwd: Path | None = None, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_cmd(["skillhost", *args], cwd=cwd, input_text=input_text, check=check)


def clone_real_project(repo_name: str) -> Path:
    REAL_CHECKOUT_ROOT.mkdir(parents=True, exist_ok=True)
    dest = REAL_CHECKOUT_ROOT / repo_name
    if dest.exists():
        shutil.rmtree(dest)
    run_cmd(["git", "clone", PROJECT_REPOS[repo_name], str(dest)])
    return dest


def manifest_path(agent: str) -> Path:
    return USER_AGENT_DIRS[agent] / ".skillhost-links.json"


def load_manifest(agent: str) -> dict:
    path = manifest_path(agent)
    if not path.exists():
        return {"version": 1, "links": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def remove_manifest_links_for_repos(repo_names: set[str]) -> None:
    for target in USER_AGENT_DIRS.values():
        manifest_file = target / ".skillhost-links.json"
        if not manifest_file.exists():
            continue
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        changed = False
        for name, record in list(manifest.get("links", {}).items()):
            if record.get("repo") in repo_names:
                link = target / name
                if link.is_symlink():
                    link.unlink()
                manifest["links"].pop(name, None)
                changed = True
        if changed:
            target.mkdir(parents=True, exist_ok=True)
            manifest_file.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def remove_config_entries(repo_names: set[str], project_names: set[str]) -> None:
    config_file = Path.home() / ".skillhost" / "config.json"
    if not config_file.exists():
        return
    config = json.loads(config_file.read_text(encoding="utf-8"))
    user_repos = config.get("user_repos")
    if isinstance(user_repos, dict):
        for repo_name in repo_names:
            user_repos.pop(repo_name, None)
    projects = config.get("projects")
    if isinstance(projects, dict):
        for project_name in project_names:
            projects.pop(project_name, None)
    config_file.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cleanup_real_fixture_state() -> None:
    repo_names = set(SKILL_REPOS)
    project_names = set(PROJECT_REPOS)
    for repo_name in sorted(repo_names):
        run_skillhost(["remove", repo_name], check=False)
    for project_name in sorted(project_names):
        run_skillhost(["unregister", "--project", project_name], check=False)
    remove_manifest_links_for_repos(repo_names)
    for repo_name in repo_names:
        shutil.rmtree(Path.home() / ".skillhost" / "user_repos" / repo_name, ignore_errors=True)
    for project_name in project_names:
        shutil.rmtree(Path.home() / ".skillhost" / "project_repos" / project_name, ignore_errors=True)
    shutil.rmtree(REAL_CHECKOUT_ROOT, ignore_errors=True)
    remove_config_entries(repo_names, project_names)


@pytest.fixture(autouse=True)
def real_fixture_state_cleanup():
    cleanup_real_fixture_state()
    yield
    cleanup_real_fixture_state()


def assert_user_linked(agent: str, repo_name: str, skill_name: str) -> None:
    link = USER_AGENT_DIRS[agent] / skill_name
    assert link.is_symlink(), f"missing symlink: {link}"
    resolved = link.resolve()
    assert repo_name in str(resolved)
    assert resolved.name == skill_name
    record = load_manifest(agent)["links"][skill_name]
    assert record["repo"] == repo_name
    assert record["scope"] == "user"


def assert_user_not_linked(agent: str, skill_name: str) -> None:
    link = USER_AGENT_DIRS[agent] / skill_name
    assert not link.exists(), f"unexpected existing path: {link}"
    assert not link.is_symlink(), f"unexpected symlink: {link}"
    assert load_manifest(agent).get("links", {}).get(skill_name, {}).get("repo") not in set(SKILL_REPOS)


def discover_installed_skill_names(repo_name: str) -> list[str]:
    repo_dir = Path.home() / ".skillhost" / "user_repos" / repo_name
    names = sorted(path.parent.name for path in repo_dir.glob("*/SKILL.md"))
    if not names:
        raise AssertionError(f"No SKILL.md files discovered in real repo: {repo_dir}")
    return names


@pytest.mark.real_e2e
def test_real_user_skill_repos_add_relink_clean_against_public_fixture_repos():
    first_repo = "skill-collection-study"
    add = run_skillhost(["add", SKILL_REPOS[first_repo]], input_text="1,4,5\n")
    assert f"Added repo '{first_repo}'." in add.stdout
    assert "Choose targets (comma-separated, default All):" in add.stdout
    assert "3 skills added." in add.stdout

    skill_names = discover_installed_skill_names(first_repo)
    assert EXPECTED_SKILLS[first_repo] == set(skill_names)
    for skill_name in skill_names:
        assert_user_linked("codex", first_repo, skill_name)
        assert_user_linked("openclaw", first_repo, skill_name)
        assert_user_linked("hermes", first_repo, skill_name)
        assert_user_not_linked("claude", skill_name)
        assert_user_not_linked("opencode", skill_name)

    relink = run_skillhost(["relink", first_repo], input_text="2,3\n")
    assert "Choose targets (comma-separated, default All):" in relink.stdout
    for skill_name in skill_names:
        assert_user_linked("claude", first_repo, skill_name)
        assert_user_linked("opencode", first_repo, skill_name)

    second_repo = "skill-collection-life"
    add_second = run_skillhost(["add", SKILL_REPOS[second_repo]], input_text="\n")
    assert f"Added repo '{second_repo}'." in add_second.stdout
    assert "3 skills added." in add_second.stdout
    assert EXPECTED_SKILLS[second_repo] == set(discover_installed_skill_names(second_repo))

    repo_dir = Path.home() / ".skillhost" / "user_repos" / first_repo
    assert repo_dir.is_dir()
    shutil.rmtree(repo_dir)

    clean = run_skillhost(["clean"])
    assert "Cleaned" in clean.stdout
    for skill_name in skill_names:
        for agent in USER_AGENT_DIRS:
            assert_user_not_linked(agent, skill_name)


@pytest.mark.real_e2e
def test_real_project_repo_register_add_project_skills_and_clean_public_fixtures():
    project_name = "project-a"
    project_dir = clone_real_project(project_name)
    run_skillhost(["register", "--project", project_name, "--git", PROJECT_REPOS[project_name]])

    repo_name = PROJECT_SKILL_REPO
    add = run_skillhost(["add", SKILL_REPOS[repo_name], "--project", project_name], cwd=project_dir, input_text="6\n")
    assert f"Added repo '{repo_name}'." in add.stdout
    assert "4 skills added." in add.stdout

    for skill_name in EXPECTED_SKILLS[repo_name]:
        for relative_target in PROJECT_AGENT_DIRS.values():
            link = project_dir / relative_target / skill_name
            assert link.is_symlink(), f"missing project symlink: {link}"
            assert repo_name in str(link.resolve())
        for user_target in USER_AGENT_DIRS.values():
            assert not (user_target / skill_name).is_symlink()

    shutil.rmtree(Path.home() / ".skillhost" / "project_repos" / project_name / repo_name)
    clean = run_skillhost(["clean"], cwd=project_dir)
    assert "Cleaned" in clean.stdout
    for skill_name in EXPECTED_SKILLS[repo_name]:
        for relative_target in PROJECT_AGENT_DIRS.values():
            link = project_dir / relative_target / skill_name
            assert not link.exists()
            assert not link.is_symlink()
