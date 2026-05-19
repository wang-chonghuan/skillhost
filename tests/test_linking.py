from pathlib import Path

from skillhost.discovery import Skill
from skillhost.linking import link_skills, load_manifest, unlink_scope


def skill(tmp_path: Path, name: str, repo: str = "repo", content: str = "") -> Skill:
    src = tmp_path / repo / name
    src.mkdir(parents=True, exist_ok=True)
    (src / "SKILL.md").write_text(content or f"# {name}", encoding="utf-8")
    return Skill(name=name, source_path=src, repo_name=repo, scope="user")


def test_link_creates_symlink_and_manifest(tmp_path):
    s = skill(tmp_path, "foo")
    target = tmp_path / "target"
    failures = link_skills([s], {"codex": target}, "user")
    assert failures == 0
    assert (target / "foo").is_symlink()
    assert (target / "foo").resolve() == s.source_path.resolve()
    manifest = load_manifest(target)
    assert manifest["links"]["foo"]["repo"] == "repo"


def test_does_not_overwrite_existing_real_directory(tmp_path):
    s = skill(tmp_path, "foo")
    target = tmp_path / "target"
    (target / "foo").mkdir(parents=True)
    failures = link_skills([s], {"codex": target}, "user")
    assert failures == 1
    assert not (target / "foo").is_symlink()


def test_updates_skillhost_managed_link_from_same_repo(tmp_path):
    s1 = skill(tmp_path, "foo", repo="repo")
    moved = tmp_path / "repo" / "moved-foo"
    moved.mkdir(parents=True)
    (moved / "SKILL.md").write_text("# moved", encoding="utf-8")
    s2 = Skill(name="foo", source_path=moved, repo_name="repo", scope="user")
    target = tmp_path / "target"
    link_skills([s1], {"codex": target}, "user")
    failures = link_skills([s2], {"codex": target}, "user")
    assert failures == 0
    assert (target / "foo").resolve() == s2.source_path.resolve()
    assert load_manifest(target)["links"]["foo"]["repo"] == "repo"


def test_detects_duplicate_skill_names(tmp_path):
    s1 = skill(tmp_path, "foo", repo="repo1")
    s2 = skill(tmp_path, "foo", repo="repo2")
    target = tmp_path / "target"
    failures = link_skills([s1, s2], {"codex": target}, "user")
    assert failures == 1
    assert not (target / "foo").exists()


def test_unlink_only_removes_manifest_managed_symlinks(tmp_path):
    s = skill(tmp_path, "foo")
    target = tmp_path / "target"
    link_skills([s], {"codex": target}, "user")
    (target / "user-owned").mkdir()
    removed = unlink_scope({"codex": target}, "user")
    assert removed == 1
    assert not (target / "foo").exists()
    assert (target / "user-owned").is_dir()
    assert load_manifest(target)["links"] == {}
