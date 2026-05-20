# SkillHost

Install Agent Skills from Git repos into Codex, Claude Code, and OpenCode using symlinks.

SkillHost is intentionally small:

- Git is the distribution system.
- Symlinks are the install system.
- No registry, no server, no account.
- Manifest files make unlink and remove safe.

The tool website is **skillhost.dev**.

## Install

```sh
pipx install skillhost
uv tool install skillhost
pip install skillhost
```

From a checkout you can also run:

```sh
pipx install .
uv tool install .
pip install .
```

## User-level skills

User-level skills are shared across projects.

```sh
skillhost add git@github.com:your-org/company-skills.git
```

After cloning, SkillHost discovers `SKILL.md` files and asks where to link them:

```text
Codex user skills:       ~/.agents/skills
Claude Code user skills: ~/.claude/skills
OpenCode user skills:    ~/.config/opencode/skills
All supported agents
Custom directory
Skip linking
```

For scripts and CI, choose the target explicitly:

```sh
skillhost add git@github.com:your-org/company-skills.git --agent codex --yes
skillhost add git@github.com:your-org/company-skills.git --target-dir ~/custom-skills --yes
```

Update pulls the latest Git changes. With no selectors, it updates all known user and project repos:

```sh
skillhost update
skillhost update --user_repos company-skills
skillhost update --project_repos my-project/project-skills
skillhost update --user_repos company-skills --agent codex --yes
```

Link or unlink all registered user-level repos at any time:

```sh
skillhost link
skillhost link --agent codex
skillhost link --target-dir /path/to/skills
skillhost unlink --agent claude --dry-run
skillhost list
skillhost doctor
```

`--agent` and `--target-dir` are mutually exclusive. Custom target directories get their own `.skillhost-links.json` manifests.

## Project-level skills

Project-level skills are linked into the current Git repository checkout. There is no full-disk search and no automatic discovery across all checkouts.

```sh
cd ~/code/my-project
skillhost project register my-project --git git@github.com:your-org/my-project.git
skillhost project add git@github.com:your-org/my-project-skills.git --project my-project
skillhost project link
```

`skillhost project link` determines the current Git repository root with Git, reads the origin remote, normalizes it, and matches it against registered project remotes. If it cannot match the current directory, register the project first.

## Target directories

User targets:

- Codex: `~/.agents/skills`
- Claude Code: `~/.claude/skills`
- OpenCode: `~/.config/opencode/skills`

Project targets:

- Codex: `.agents/skills`
- Claude Code: `.claude/skills`
- OpenCode: `.opencode/skills`

SkillHost uses each agent's native target directory. It does not rely on one agent reading another agent's directory.

## Source repository layouts

Single skill repo:

```text
my-skill/
  SKILL.md
```

Skill collection repo:

```text
company-skills/
  skills/
    git/
      SKILL.md
    db/
      SKILL.md
```

Flat collection repo:

```text
company-skills/
  git/
    SKILL.md
  db/
    SKILL.md
```

Skill discovery is shallow and only considers valid skills that contain `SKILL.md`. It does not recursively scan references, assets, examples, scripts, docs, or tests.

## Frontmatter

A `SKILL.md` can include simple YAML-style frontmatter:

```md
---
name: ng-git
description: Narrative git workflow helpers
---
```

Skill names must contain only lowercase letters, digits, and hyphens. If no name is present, SkillHost uses the skill directory or repo name.

## Conflict policy

- Existing user-owned skills are never overwritten.
- Duplicate skill names across source repos are skipped and reported.
- `unlink` only removes SkillHost-managed symlinks recorded in `.skillhost-links.json`.
- `remove` unlinks manifest-managed symlinks before deleting a user repo; dirty repos are refused unless `--force` is used.

## Security

SkillHost never executes code from skill repositories. It only:

1. clones repositories with Git,
2. updates repositories with `git pull --ff-only`,
3. reads `SKILL.md` metadata, and
4. creates or removes manifest-managed symlinks.

SkillHost does not implement registry support, semver, package resolution, full-disk project discovery, or auto-running skill scripts.
