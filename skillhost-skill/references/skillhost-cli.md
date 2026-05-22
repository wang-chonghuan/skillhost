# SkillHost CLI Reference

## Core Model

SkillHost installs agent skills from Git repositories by cloning or updating repos under SkillHost state and creating manifest-tracked symlinks into agent skill directories. Git is the source of truth for skill content. SkillHost does not execute skill repository code and does not overwrite unmanaged files or directories.

No initialization command is required. Commands create `~/.skillhost` state on demand.

Default state:

```text
~/.skillhost/
  config.json
  user_repos/<repo-name>/
  project_repos/<project-name>/<repo-name>/
```

Each target directory has `.skillhost-links.json` for links that SkillHost owns.

## Agents and Targets

Built-in user targets:

```text
codex    ~/.agents/skills
claude   ~/.claude/skills
opencode ~/.config/opencode/skills
openclaw ~/.openclaw/skills
hermes   ~/.hermes/skills
```

Built-in project targets:

```text
codex    .agents/skills
claude   .claude/skills
opencode .opencode/skills
```

OpenClaw and Hermes are user-level only unless a custom agent is registered with a project target.

## Command Map

Install or upgrade:

```sh
pipx install skillhost
uv tool install skillhost
pip install skillhost
skillhost upgrade
```

Inspect:

```sh
skillhost --version
skillhost agents
skillhost projects
skillhost config
skillhost doctor [--project <name>]
skillhost list [--agent codex|claude|opencode|openclaw|hermes]
skillhost list --all
```

Manage user-level skill repos:

```sh
skillhost add <skill-git-repo> [--name <repo-name>]
skillhost update [repo-name] [--agent codex|claude|opencode|openclaw|hermes]
skillhost relink [repo-name] [--agent codex|claude|opencode|openclaw|hermes]
skillhost unlink <repo-name> [--agent codex|claude|opencode|openclaw|hermes]
skillhost unlink --all [--agent codex|claude|opencode|openclaw|hermes]
skillhost remove <repo-name>
skillhost clean
```

Manage project-level skill repos:

```sh
skillhost register --project <name> --git <project-git-url>
cd /path/to/project-checkout
skillhost add <skill-git-repo> --project <name> [--name <repo-name>]
skillhost update [repo-name] --project <name> [--agent codex|claude|opencode]
skillhost relink [repo-name] --project <name> [--agent codex|claude|opencode]
skillhost unlink <repo-name> --project <name> [--agent codex|claude|opencode]
skillhost remove <repo-name> --project <name>
```

Register custom agents:

```sh
skillhost register --agent <name> --user-dir <path> [--project-dir <relative-path>]
skillhost unregister --agent <name>
skillhost agents
skillhost relink
```

## Natural-Language Routing

"Add this skill repo" means `skillhost add <git-url>`. If the user wants only specific agents and the CLI prompts, provide the menu choice interactively or pipe the numeric choice in a non-interactive run. Built-in target choices are ordered Codex, Claude Code, OpenCode, OpenClaw, Hermes Agent, All.

"Update", "sync", or "pull skills" means `skillhost update`, optionally with a repo name, project, or agent. Update removes stale SkillHost-managed links for selected targets, runs `git pull --ff-only`, and relinks.

"Make the agent see skills again" often means `skillhost relink`, optionally with a repo name or `--agent`. Relink recreates manifest-managed symlinks without pulling Git changes.

"Hide/show skills for an agent" means `skillhost list --agent <agent>` in an interactive terminal. In the menu, selected means visible and unselected means hidden. Hidden choices are persisted in `config.json` and later respected by `update` and `relink`.

"Remove a skill repo" means `skillhost remove <repo-name>`, not deleting target directories by hand. It unlinks SkillHost-managed links, deletes the local clone under SkillHost state, and removes the repo from config.

"Stop linking this repo but keep the clone" means `skillhost unlink <repo-name>`. Use `--all` only when the user explicitly wants all SkillHost-managed links removed for the selected scope and target.

"Why can't my agent see a skill?" means inspect `skillhost list --agent <agent>`, `skillhost list --all`, `skillhost doctor`, and the target directory for that agent. Common causes are hidden visibility config, stale or broken symlinks, adding to a different agent target, project scope mismatch, duplicate skill names, or an unmanaged file already occupying the target path.

## Skill Repository Shapes

Single skill repo:

```text
my-skill/
  SKILL.md
```

Collection under `skills/`:

```text
company-skills/
  skills/
    git/
      SKILL.md
    db/
      SKILL.md
```

Small flat collection:

```text
company-skills/
  git/
    SKILL.md
  db/
    SKILL.md
```

Discovery is intentionally shallow: root `SKILL.md`, direct children under `skills/`, and direct children under the repo root. Hidden directories and obvious non-skill directories such as `tests`, `docs`, `examples`, `scripts`, `references`, and `assets` are ignored.

## Safety and Troubleshooting

SkillHost removes only manifest-managed symlinks. It does not delete user-owned skill directories. It uses `git pull --ff-only`; if the repo is dirty or needs a merge, surface that directly instead of forcing Git history changes.

Use `skillhost clean` for broken SkillHost-managed symlinks and stale manifest entries. Use `skillhost doctor` before manual edits. Manual changes to `~/.skillhost/config.json` should be a last resort.
