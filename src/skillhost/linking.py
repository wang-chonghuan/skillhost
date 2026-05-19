"""Manifest-managed symlink creation and removal."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from .discovery import Skill
from .errors import SkillhostError

MANIFEST = ".skillhost-links.json"


def load_manifest(target_dir: str | Path) -> dict:
    path = Path(target_dir) / MANIFEST
    if not path.exists():
        return {"version": 1, "links": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SkillhostError(f"Invalid manifest: {path}") from exc
    data.setdefault("version", 1)
    data.setdefault("links", {})
    return data


def save_manifest(target_dir: str | Path, manifest: dict) -> None:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _record(skill: Skill, agent: str) -> dict[str, str | None]:
    return {
        "source": str(skill.source_path.resolve()),
        "scope": skill.scope,
        "repo": skill.repo_name,
        "agent": agent,
        "project": skill.project,
    }


def _duplicates(skills: list[Skill]) -> set[str]:
    seen: dict[str, Skill] = {}
    dupes: set[str] = set()
    for skill in skills:
        if skill.name in seen:
            dupes.add(skill.name)
        else:
            seen[skill.name] = skill
    return dupes


def link_skills(
    skills: list[Skill],
    targets: dict[str, Path],
    scope: str,
    project: str | None = None,
    dry_run: bool = False,
) -> int:
    """Link skills to targets. Returns conflict/skip count."""
    duplicate_names = _duplicates(skills)
    failures = 0
    for name in sorted(duplicate_names):
        print(f"Conflict: duplicate skill name '{name}' from multiple repos; skipping", file=sys.stderr)
        failures += 1
    linkable = [s for s in skills if s.name not in duplicate_names]

    for agent, target_dir in targets.items():
        manifest = load_manifest(target_dir)
        changed = False
        for skill in linkable:
            if skill.scope != scope or (project is not None and skill.project != project):
                continue
            dest = target_dir / skill.name
            source = str(skill.source_path.resolve())
            existing = manifest["links"].get(skill.name)
            if dest.exists() or dest.is_symlink():
                if existing and existing.get("scope") == scope and existing.get("agent") == agent:
                    same_owner = existing.get("repo") == skill.repo_name and existing.get("project") == skill.project
                    if os.path.islink(dest) and same_owner:
                        current = os.path.realpath(dest)
                        if current == source:
                            print(f"Keep {agent}:{skill.name} -> {source}")
                            continue
                        print(f"Update {agent}:{skill.name} -> {source}")
                        if not dry_run:
                            dest.unlink()
                            _create_symlink(skill.source_path, dest)
                            manifest["links"][skill.name] = _record(skill, agent)
                            changed = True
                        continue
                print(f"Warning: target exists and is not skillhost-managed; skipping {dest}", file=sys.stderr)
                failures += 1
                continue
            print(f"Link {agent}:{skill.name} -> {source}")
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                _create_symlink(skill.source_path, dest)
                manifest["links"][skill.name] = _record(skill, agent)
                changed = True
        if changed and not dry_run or not dry_run and (target_dir / MANIFEST).exists():
            save_manifest(target_dir, manifest)
    return failures


def _create_symlink(source: Path, dest: Path) -> None:
    try:
        dest.symlink_to(source.resolve(), target_is_directory=True)
    except OSError as exc:
        if os.name == "nt":
            raise SkillhostError(
                "Could not create symlink on Windows. Enable Developer Mode or run as administrator."
            ) from exc
        raise


def unlink_scope(
    targets: dict[str, Path],
    scope: str,
    project: str | None = None,
    repo_name: str | None = None,
    dry_run: bool = False,
) -> int:
    removed = 0
    for agent, target_dir in targets.items():
        manifest = load_manifest(target_dir)
        links = dict(manifest.get("links", {}))
        changed = False
        for name, record in links.items():
            if record.get("scope") != scope:
                continue
            if project is not None and record.get("project") != project:
                continue
            if repo_name is not None and record.get("repo") != repo_name:
                continue
            dest = target_dir / name
            if dest.is_symlink():
                print(f"Unlink {agent}:{name}")
                if not dry_run:
                    dest.unlink()
                removed += 1
            elif dest.exists():
                print(f"Warning: manifest entry is not a symlink, leaving in place: {dest}", file=sys.stderr)
            else:
                print(f"Remove stale manifest entry {agent}:{name}")
            if not dry_run:
                manifest["links"].pop(name, None)
                changed = True
        if changed and not dry_run:
            save_manifest(target_dir, manifest)
    return removed
