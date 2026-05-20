# SkillHost

SkillHost manages Agent Skills from Git repositories.

It keeps Git as the source of truth, symlinks as the install system, and JSON config as the persistent source of truth.

## Install

```sh
pipx install skillhost
uv tool install skillhost
pip install skillhost
```

## CLI

```text
skillhost
  init

  register --project <name> --git <project-git-url>
  unregister --project <name>

  register --agent <name> --user-dir <path> [--project-dir <path>]
  unregister --agent <name>

  add <skill-git-repo> [--project <name>] [--name <repo-name>]
  update [repo-name] [--project <name>] [--all]
  remove <repo-name> [--project <name>]

  relink [repo-name] [--project <name>] [--agent <name>] [--all]
  unlink [repo-name] [--project <name>] [--agent <name>] [--all]

  list [--project <name>]
  projects
  agents
  doctor [--project <name>]

  config
```

User scope is the default. Project scope is selected only with `--project <name>`.

## Layout

```text
~/.skillhost/
  config.json
  user_repos/
    <repo-name>/
  project_repos/
    <project-name>/
      <repo-name>/
```

`skillhost config` prints the absolute path to `config.json`.

`config.json` is the source of truth for:
- registered agents
- registered projects
- user skill repos
- project skill repos
- repo URLs
- normalized URLs
- local repo paths

Each target directory also keeps a local `.skillhost-links.json` manifest so unlink and remove only touch SkillHost-managed links.

## Examples

```sh
skillhost init

skillhost register --project nsdk --git git@github.com:your-org/nsdk.git
skillhost register --agent cursor --user-dir ~/.cursor/skills --project-dir .cursor/skills

skillhost add git@github.com:your-org/company-skills.git
skillhost add git@github.com:your-org/nsdk-skills.git --project nsdk

skillhost update
skillhost update company-skills
skillhost update --project nsdk
skillhost update --project nsdk --all

skillhost relink
skillhost relink --agent codex
skillhost relink --project nsdk
skillhost unlink company-skills --agent codex
skillhost unlink --project nsdk --all

skillhost list
skillhost list --project nsdk
skillhost projects
skillhost agents
skillhost doctor
skillhost doctor --project nsdk

skillhost remove company-skills
skillhost remove nsdk-skills --project nsdk

skillhost unregister --agent cursor
skillhost unregister --project nsdk
```

## Repository layouts

Single skill repo:

```text
my-skill/
  SKILL.md
```

Collection repo:

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

Skill discovery is shallow. SkillHost does not execute code from skill repositories.
