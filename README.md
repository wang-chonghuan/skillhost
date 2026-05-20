# SkillHost

SkillHost manages Agent Skills from Git repositories. Git repositories are the source of truth for skill content, symlinks are the install mechanism, and `~/.skillhost/config.json` is the persistent source of truth for registered agents, projects, and skill repositories.

SkillHost is intentionally small: it does not run code from skill repositories, does not scan your whole disk, and does not overwrite user-owned existing skills.

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

## Current command list

```text
skillhost [-h] [--version]
  init

  register --project <name> --git <project-git-url>
  register --agent <name> --user-dir <path> [--project-dir <path>]

  unregister --project <name>
  unregister --agent <name>

  add <skill-git-repo> [--project <name>] [--name <repo-name>]

  update [repo-name] [--project <name>] [--agent {codex,claude,opencode}] [--all]

  remove <repo-name> [--project <name>]

  relink [repo-name] [--project <name>] [--agent {codex,claude,opencode}] [--all]

  unlink [repo-name] [--project <name>] [--agent {codex,claude,opencode}] [--all]

  list [--project <name>]
  projects
  agents
  doctor [--project <name>]
  config
```

There are no `user`, `project`, `register-project`, `config path`, or `config edit` subcommands. Older flags such as `--dry-run`, `--force`, `--all-projects`, `--all-skills`, `--include`, and `--exclude` are not part of the current CLI.

## Scope model

User scope is the default. These commands operate on user-level skill repositories unless `--project <name>` is provided:

```sh
skillhost add <repo>
skillhost update
skillhost relink
skillhost unlink <repo-name>
skillhost list
skillhost doctor
skillhost remove <repo-name>
```

Project scope is selected only with `--project <name>`:

```sh
skillhost add <repo> --project nsdk
skillhost update --project nsdk
skillhost relink --project nsdk
skillhost unlink --project nsdk --all
skillhost list --project nsdk
skillhost doctor --project nsdk
skillhost remove nsdk-skills --project nsdk
```

`--all` means all skill repositories in the selected scope. For `update`, `relink`, `list`, and `doctor`, omitting `repo-name` already means all repositories in the selected scope. For `unlink`, omitting both `repo-name` and `--all` is refused to avoid accidental bulk unlinking.

## State layout

Default state lives under `~/.skillhost`:

```text
~/.skillhost/
  config.json
  user_repos/
    <repo-name>/
  project_repos/
    <project-name>/
      <repo-name>/
```

`skillhost config` prints only the absolute path to `config.json`.

`config.json` stores:

```text
version
home
agents
user_repos
projects
projects.<project>.remotes
projects.<project>.repos
repo URLs
normalized URLs
local repo paths
```

Each agent target directory also has a target-local `.skillhost-links.json` manifest. This manifest is separate from `config.json` and is used so `unlink` and `remove` only touch SkillHost-managed symlinks.

## Agent targets

Built-in agents are initialized in config:

```text
codex    user: ~/.agents/skills                 project: .agents/skills
claude   user: ~/.claude/skills                 project: .claude/skills
opencode user: ~/.config/opencode/skills        project: .opencode/skills
```

Register another agent target:

```sh
skillhost register --agent cursor --user-dir ~/.cursor/skills --project-dir .cursor/skills
skillhost agents
skillhost unregister --agent cursor
```

Agent registration updates config only. It does not link automatically; run `skillhost relink` when you want to refresh links.

## User-level workflow

```sh
skillhost init
skillhost add git@github.com:org/company-skills.git
skillhost list
skillhost update
skillhost relink
skillhost unlink company-skills --agent codex
skillhost remove company-skills
```

`add` clones the skill repository into `~/.skillhost/user_repos/<repo-name>`, records it in `config.json`, discovers skills, and relinks user-level agent targets when possible.

Use `--name` when you want the local repo name to differ from the Git URL basename:

```sh
skillhost add git@github.com:org/company-skills.git --name shared-skills
```

## Project-level workflow

First register the project remote:

```sh
skillhost register --project nsdk --git git@github.com:org/nsdk.git
```

Then run project-scoped commands from inside the matching project checkout when you want project links to be created or removed:

```sh
cd ~/code/nsdk
skillhost add git@github.com:org/nsdk-skills.git --project nsdk
skillhost update --project nsdk
skillhost relink --project nsdk
skillhost unlink --project nsdk --all
skillhost remove nsdk-skills --project nsdk
```

Project `relink` and project `unlink` validate the current Git repository root and its `origin` remote against the registered project. SkillHost does not search the disk for project checkouts and does not perform cross-project bulk cleanup.

If you add or update a project skill repository outside the matching checkout, the repository is still recorded under `~/.skillhost/project_repos/<project>/<repo-name>`, and SkillHost prints the command to run inside the project checkout.

## Command details

### `skillhost init`

Creates the default `~/.skillhost` layout and `config.json` if they do not already exist.

### `skillhost register`

```sh
skillhost register --project <name> --git <project-git-url>
skillhost register --agent <name> --user-dir <path> [--project-dir <path>]
```

Project registration normalizes and stores the project Git remote and creates `~/.skillhost/project_repos/<name>`. Agent registration stores user and project target directories. `--project` and `--agent` are mutually exclusive.

### `skillhost unregister`

```sh
skillhost unregister --project <name>
skillhost unregister --agent <name>
```

Removes the config entry only. It does not delete user-owned files and does not scan disk for unknown checkouts.

### `skillhost add`

```sh
skillhost add <skill-git-repo> [--project <name>] [--name <repo-name>]
```

Clones a skill repository into the selected scope and records it in config. Without `--name`, the repo name is derived from the Git URL basename with `.git` stripped.

### `skillhost update`

```sh
skillhost update [repo-name] [--project <name>] [--agent {codex,claude,opencode}] [--all]
```

Runs `git pull --ff-only` for one repository or all repositories in the selected scope. It does not merge or rebase. After updating, it relinks the selected scope when possible.

### `skillhost remove`

```sh
skillhost remove <repo-name> [--project <name>]
```

Unlinks SkillHost-managed symlinks for that repo where safely discoverable, deletes the cloned repo under `~/.skillhost`, and removes the repo entry from config. It does not support `--all`.

### `skillhost relink`

```sh
skillhost relink [repo-name] [--project <name>] [--agent {codex,claude,opencode}] [--all]
```

Creates or updates SkillHost-managed symlinks for one repo or all repos in the selected scope. Existing unmanaged files or directories are skipped.

### `skillhost unlink`

```sh
skillhost unlink [repo-name] [--project <name>] [--agent {codex,claude,opencode}] [--all]
```

Removes only symlinks recorded in `.skillhost-links.json`. To unlink all repos in a scope, pass `--all` explicitly:

```sh
skillhost unlink --all
skillhost unlink --project nsdk --all
```

### `skillhost list`, `projects`, `agents`, `doctor`, `config`

```sh
skillhost list [--project <name>]
skillhost projects
skillhost agents
skillhost doctor [--project <name>]
skillhost config
```

`list` shows repos and discovered skills in the selected scope. `projects` shows registered projects and normalized remotes. `agents` shows registered agent user/project target directories. `doctor` checks config, repos, duplicate skill names, targets, manifests, broken symlinks, and missing sources. `config` prints the absolute config path only.

## Supported skill repository layouts

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

Skill discovery is shallow. SkillHost checks root `SKILL.md`, direct children under `skills/`, or direct children under the repo root. It ignores hidden directories and obvious non-skill directories such as `tests`, `docs`, `examples`, `scripts`, `references`, and `assets`.

## Git URL normalization

Common SSH and HTTPS Git URL forms normalize to `host/org/repo`:

```text
git@github.com:org/repo.git      -> github.com/org/repo
git@github.com:org/repo          -> github.com/org/repo
https://github.com/org/repo.git  -> github.com/org/repo
https://github.com/org/repo      -> github.com/org/repo
ssh://git@github.com/org/repo.git -> github.com/org/repo
```

Project matching uses the current Git root plus `git remote get-url origin`, normalized with the same rules.

## Safety rules

SkillHost does not execute code from skill repositories. It only clones repositories, pulls with `git pull --ff-only`, reads `SKILL.md` metadata, and creates or removes manifest-managed symlinks.

SkillHost never overwrites unmanaged existing targets, never removes user-owned skill directories, and never performs full-disk project discovery or cross-project bulk operations.
