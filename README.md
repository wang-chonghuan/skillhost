# SkillHost

Website: https://skillhost.dev
GitHub: https://github.com/wang-chonghuan/skillhost

SkillHost installs Agent Skills from Git repositories into local agent skill directories by creating safe, manifest-tracked symlinks.

Git is the source of truth. SkillHost clones or pulls skill repos, discovers `SKILL.md` files, and links the discovered skills into agents such as Codex and Claude Code. It does not execute code from skill repositories and does not overwrite unmanaged files.

## What's new in 0.1.8

SkillHost 0.1.8 adds per-agent skill visibility controls through `skillhost list --agent <name>`, persists hidden skills in config, keeps hidden skills hidden during later `update` and `relink`, and includes a `skillhost-skill` agent skill for guiding SkillHost usage.

## Typical path

```sh
pipx install skillhost

skillhost add git@github.com:org/company-skills.git
# choose Codex, Claude Code, OpenCode, OpenClaw, Hermes Agent, or All

skillhost update
skillhost list
```

Result:

```text
skill repo            -> SkillHost -> ~/.agents/skills
skill collection repo -> SkillHost -> ~/.claude/skills
                                  -> teammate ~/.agents/skills
```

No `skillhost init` is required. Commands create the needed `~/.skillhost` state on demand.

## Install

```sh
pipx install skillhost
uv tool install skillhost
pip install skillhost
```

From a checkout:

```sh
uv tool install .
pip install .
```

Upgrade SkillHost itself:

```sh
skillhost upgrade
```

`upgrade` detects common installers. It uses `pipx upgrade skillhost` for pipx installs, `uv tool upgrade skillhost` for uv tool installs, and falls back to `python -m pip install --upgrade skillhost`.

## Core commands

```sh
skillhost add <skill-git-repo> [--project <name>] [--name <repo-name>]
skillhost update [repo-name] [--project <name>] [--agent codex|claude|opencode|openclaw|hermes] [--all]
skillhost relink [repo-name] [--project <name>] [--agent codex|claude|opencode|openclaw|hermes] [--all]
skillhost unlink [repo-name] [--project <name>] [--agent codex|claude|opencode|openclaw|hermes] [--all]
skillhost remove <repo-name> [--project <name>]
skillhost clean
skillhost list [--project <name>] [--agent codex|claude|opencode|openclaw|hermes] [--all]
skillhost doctor [--project <name>]
skillhost agents
skillhost projects
skillhost config
```

Useful behavior:

- `add` clones a skill repo, discovers skills, then asks which agent directories to link into.
- `update` uses the same target selection flow as `add`, removes stale SkillHost-managed links for the selected targets, runs `git pull --ff-only`, then relinks.
- `relink` recreates manifest-managed symlinks without pulling.
- `unlink` removes only SkillHost-managed symlinks recorded in `.skillhost-links.json`.
- `remove` unlinks, deletes the local clone under `~/.skillhost`, and removes the repo from config.
- `clean` removes broken SkillHost-managed symlinks and stale manifest entries.
- `list` shows skills visible to the selected agent, defaulting to Codex. In an interactive terminal, select skills to hide or show for that agent. `--all` shows registered repos and discovered skills.
- `doctor` checks config, repos, duplicate skill names, targets, manifests, broken links, and missing sources.
- `config` prints the config file path only.

Use `--all` when a command needs an explicit all-repos operation, especially `unlink --all`.

## Agent targets

Built-in targets:

```text
codex    user: ~/.agents/skills           project: .agents/skills
claude   user: ~/.claude/skills           project: .claude/skills
opencode user: ~/.config/opencode/skills  project: .opencode/skills
openclaw user: ~/.openclaw/skills         project: —
hermes   user: ~/.hermes/skills           project: —
```

Register a custom agent:

```sh
skillhost register --agent cursor --user-dir ~/.cursor/skills --project-dir .cursor/skills
skillhost agents
skillhost relink
```

Agent registration updates config only. Run `skillhost relink` when you want to create or refresh links.

## Skill repo shapes

A skill repo contains one skill:

```text
my-skill/
  SKILL.md
```

A skill collection repo contains multiple skills:

```text
company-skills/
  skills/
    git/
      SKILL.md
    db/
      SKILL.md
```

Small flat collections are also supported:

```text
company-skills/
  git/
    SKILL.md
  db/
    SKILL.md
```

Discovery is intentionally shallow. SkillHost checks root `SKILL.md`, direct children under `skills/`, and direct children under the repo root. It ignores hidden directories and obvious non-skill directories such as `tests`, `docs`, `examples`, `scripts`, `references`, and `assets`.

## Project skills

Project skills are scoped to a registered project repository and linked into project-local agent directories.

```sh
skillhost register --project my-project --git git@github.com:org/my-project.git
cd /path/to/my-project
skillhost add git@github.com:org/my-project-skills.git --project my-project
skillhost update --project my-project
```

Project links go to directories such as:

```text
.agents/skills
.claude/skills
.opencode/skills
```

SkillHost validates the current Git root and `origin` remote against the registered project. It does not scan your disk for checkouts.

## State and safety

Default state:

```text
~/.skillhost/
  config.json
  user_repos/<repo-name>/
  project_repos/<project-name>/<repo-name>/
```

Each agent target directory also gets a local `.skillhost-links.json` manifest. This is how SkillHost knows which symlinks it owns.

Safety rules:

- Does not execute code from skill repositories.
- Does not overwrite unmanaged existing files or directories.
- Does not delete user-owned skill directories.
- Removes only manifest-managed symlinks.
- Uses `git pull --ff-only` for updates; it does not merge or rebase.
- Does not perform full-disk project discovery or cross-project bulk cleanup.

## Git URL handling

Common SSH and HTTPS Git URL forms normalize to the same repo identity:

```text
git@github.com:org/repo.git       -> github.com/org/repo
git@github.com:org/repo           -> github.com/org/repo
https://github.com/org/repo.git   -> github.com/org/repo
https://github.com/org/repo       -> github.com/org/repo
ssh://git@github.com/org/repo.git -> github.com/org/repo
```
