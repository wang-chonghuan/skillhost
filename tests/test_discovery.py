from pathlib import Path

import pytest

from skillhost.discovery import discover_skills_in_repo, parse_frontmatter
from skillhost.errors import SkillhostError


def write_skill(path: Path, text: str = "# Skill") -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(text, encoding="utf-8")


def test_single_skill_repo_with_frontmatter(tmp_path):
    write_skill(tmp_path, "---\nname: single-skill\ndescription: Does things\n---\nBody")
    skills = discover_skills_in_repo(tmp_path, "repo-name", "user")
    assert [s.name for s in skills] == ["single-skill"]
    assert skills[0].description == "Does things"
    assert skills[0].source_path == tmp_path.resolve()


def test_collection_repo_skills_dir(tmp_path):
    write_skill(tmp_path / "skills" / "foo")
    write_skill(tmp_path / "skills" / "bar")
    skills = discover_skills_in_repo(tmp_path, "repo", "user")
    assert [s.name for s in skills] == ["bar", "foo"]


def test_flat_collection_and_no_deep_recursion(tmp_path):
    write_skill(tmp_path / "foo")
    write_skill(tmp_path / "docs" / "ignored")
    write_skill(tmp_path / "nested" / "too-deep")
    skills = discover_skills_in_repo(tmp_path, "repo", "project", "proj")
    assert [s.name for s in skills] == ["foo"]
    assert skills[0].project == "proj"


def test_frontmatter_fallback_to_dir_name(tmp_path):
    write_skill(tmp_path / "foo", "# No frontmatter")
    assert parse_frontmatter(tmp_path / "foo" / "SKILL.md") == {}
    skills = discover_skills_in_repo(tmp_path, "repo", "user")
    assert skills[0].name == "foo"


def test_invalid_skill_name_rejected(tmp_path):
    write_skill(tmp_path, "---\nname: Bad_Name\n---\n")
    with pytest.raises(SkillhostError):
        discover_skills_in_repo(tmp_path, "repo", "user")
