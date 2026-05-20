You are working in the existing `skillhost` repository.

This repository already has a working/basic version of the SkillHost CLI. Your task is to refactor the existing implementation to match the final product and CLI design below.

Do not rewrite the project from scratch unless a module is truly simpler to replace than to patch. Prefer incremental refactoring, preserve useful existing code, and update tests/docs accordingly.

Product name:
SkillHost

Python package / CLI command:
skillhost

Product purpose:
SkillHost manages Agent Skills from Git repositories.

It solves:
- skill sharing across AI agents, teammates, and projects
- skill updates through Git
- clean separation between user-level skills and project-level skills
- avoiding manual copy-paste installs
- avoiding stale skill files
- avoiding global/project scope confusion

Core principles:
- SSOT: Git repositories are the source of truth for skill content.
- One way to do one thing.
- User-level scope is the default.
- Project-level scope is selected only with `--project <name>`.
- Git is the distribution system.
- Symlinks are the install system.
- JSON config is the persistent source of truth.
- Target-local link manifests make unlink/remove safe.
- Do not execute code from skill repositories.
- Do not overwrite user-owned existing skills.
- Do not scan the full disk.
- Do not implement cross-project bulk operations.
- Do not add optional flags not listed in this spec.

Final CLI command surface:

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

Remove or reject all older/alternative command styles:
- skillhost user ...
- skillhost project ...
- skillhost register-project
- skillhost project register
- skillhost add --project-git
- skillhost config path
- skillhost config edit
- --all-projects
- --all-skills
- --dry-run
- --force
- --include
- --exclude

If older command variants still exist, remove them. If keeping temporary compatibility is easier, make them fail with a short message pointing to the final command.

Command semantics:

1. Scope

Default scope is user-level.

These operate on user-level skill repos:

  skillhost add <repo>
  skillhost update
  skillhost relink
  skillhost list
  skillhost doctor

Project-level scope is selected only with:

  --project <name>

Examples:

  skillhost add <repo> --project nsdk
  skillhost update --project nsdk
  skillhost relink --project nsdk
  skillhost list --project nsdk
  skillhost doctor --project nsdk

2. --all

There is exactly one `--all` flag.

Meaning:

  --all = all skill repos in the selected scope

Selected scope:
- no --project: all user-level skill repos
- with --project <name>: all skill repos for that project

Do not implement all-projects behavior.

Allowed examples:

  skillhost update --all
  skillhost update --project nsdk --all
  skillhost relink --all
  skillhost relink --project nsdk --all
  skillhost unlink --all
  skillhost unlink --project nsdk --all

Also allow these convenient defaults:

  skillhost update
  skillhost relink
  skillhost list
  skillhost doctor

For update/relink/list/doctor:
- no repo-name means all repos in selected scope.

For unlink:
- if no repo-name and no --all, refuse.
- print:
  Refusing to unlink all links implicitly. Use --all.

For remove:
- repo-name is required.
- remove does not support --all.

3. Persistent layout

Use this default structure:

  ~/.skillhost/
    config.json
    user_repos/
      <repo-name>/
    project_repos/
      <project-name>/
        <repo-name>/

Use absolute expanded paths in config.json.

4. Config file

Use JSON, not TOML.

Config path:

  ~/.skillhost/config.json

The command:

  skillhost config

must only print the absolute path to the config file.

Do not provide:
- skillhost config path
- skillhost config edit
- editor opening behavior

Config is the SSOT for:
- registered agents
- registered projects
- user skill repos
- project skill repos
- repo URLs
- normalized URLs
- local repo paths

Use schema version 1.

Example config.json:

{
  "version": 1,
  "home": "/Users/me/.skillhost",
  "agents": {
    "codex": {
      "enabled": true,
      "user_dir": "/Users/me/.agents/skills",
      "project_dir": ".agents/skills",
      "builtin": true
    },
    "claude": {
      "enabled": true,
      "user_dir": "/Users/me/.claude/skills",
      "project_dir": ".claude/skills",
      "builtin": true
    },
    "opencode": {
      "enabled": true,
      "user_dir": "/Users/me/.config/opencode/skills",
      "project_dir": ".opencode/skills",
      "builtin": true
    }
  },
  "user_repos": {
    "company-skills": {
      "url": "git@github.com:org/company-skills.git",
      "normalized_url": "github.com/org/company-skills",
      "path": "/Users/me/.skillhost/user_repos/company-skills"
    }
  },
  "projects": {
    "nsdk": {
      "remotes": [
        "github.com/org/nsdk"
      ],
      "repos": {
        "nsdk-skills": {
          "url": "git@github.com:org/nsdk-skills.git",
          "normalized_url": "github.com/org/nsdk-skills",
          "path": "/Users/me/.skillhost/project_repos/nsdk/nsdk-skills"
        }
      }
    }
  }
}

If the current implementation has an older config format, implement a simple migration into this JSON shape where possible. If migration is too risky, preserve old data by backing it up and creating the new config.

5. Link manifest

Do not merge config.json with link manifest files.

They have different responsibilities:

  ~/.skillhost/config.json
    global source-of-truth config

  <target-skill-dir>/.skillhost-links.json
    target-local generated manifest for safe unlink/remove

Each agent target directory must maintain its own `.skillhost-links.json`.

Examples:

  ~/.agents/skills/.skillhost-links.json
  ~/.claude/skills/.skillhost-links.json
  ~/.config/opencode/skills/.skillhost-links.json

  <project-root>/.agents/skills/.skillhost-links.json
  <project-root>/.claude/skills/.skillhost-links.json
  <project-root>/.opencode/skills/.skillhost-links.json

Manifest schema:

{
  "version": 1,
  "links": {
    "ng-git": {
      "source": "/Users/me/.skillhost/user_repos/company-skills/skills/ng-git",
      "scope": "user",
      "repo": "company-skills",
      "agent": "codex"
    },
    "nf-airflow": {
      "source": "/Users/me/.skillhost/project_repos/nsdk/nsdk-skills/skills/nf-airflow",
      "scope": "project",
      "project": "nsdk",
      "repo": "nsdk-skills",
      "agent": "codex"
    }
  }
}

Rules:
- Only remove symlinks recorded in target-local manifest.
- If target exists and is not manifest-managed, skip it.
- Never overwrite user-owned directories.
- If duplicate skill names are discovered in selected scope, report conflict and skip that skill.
- Link creation should write/update manifest.
- Unlink should remove manifest entries after deleting symlinks.

6. Built-in agents

Initialize these built-in agents by default:

codex:
  user_dir: ~/.agents/skills
  project_dir: .agents/skills
  builtin: true

claude:
  user_dir: ~/.claude/skills
  project_dir: .claude/skills
  builtin: true

opencode:
  user_dir: ~/.config/opencode/skills
  project_dir: .opencode/skills
  builtin: true

Use expanded absolute paths for user_dir in config.
Keep project_dir relative.

7. init

  skillhost init

Behavior:
- create ~/.skillhost/
- create ~/.skillhost/config.json if missing
- create user_repos and project_repos directories
- initialize built-in agents if config is new
- do not clone repos
- do not link anything
- safe to run multiple times

8. register / unregister

register is only for context configuration.

Project registration:

  skillhost register --project nsdk --git git@github.com:org/nsdk.git

Behavior:
- normalize project Git URL
- create/update project entry in config
- create ~/.skillhost/project_repos/nsdk
- do not add skill repos
- do not link anything

Agent registration:

  skillhost register --agent cursor --user-dir ~/.cursor/skills --project-dir .cursor/skills

Behavior:
- register/update an agent target
- require at least --user-dir or --project-dir
- do not link automatically
- after success, print a short hint:
  Run `skillhost relink` to refresh user-level links.

Unregister:

  skillhost unregister --project nsdk
  skillhost unregister --agent cursor

Behavior:
- remove config entry
- do not scan disk
- do not delete user-owned files
- do not perform full cleanup across unknown project checkouts
- be conservative

9. add

User-level:

  skillhost add git@github.com:org/company-skills.git
  skillhost add git@github.com:org/company-skills.git --name company-skills

Project-level:

  skillhost add git@github.com:org/nsdk-skills.git --project nsdk

Behavior:
- clone skill repo into selected scope
- user path:
  ~/.skillhost/user_repos/<repo-name>
- project path:
  ~/.skillhost/project_repos/<project-name>/<repo-name>
- if --name is provided, use it as repo-name
- otherwise derive repo-name from Git URL basename, stripping .git
- record repo in config
- discover skills
- automatically relink after add when possible

Project add:
- project must already be registered
- do not auto-register project from add
- if current directory is inside a matching registered project checkout, link into that project root
- if current directory does not match, still add the repo but print:
  Added project skill repo for <project>.
  Run inside the project checkout:
    skillhost relink --project <project>

10. update

Examples:

  skillhost update
  skillhost update company-skills
  skillhost update --all

  skillhost update --project nsdk
  skillhost update nsdk-skills --project nsdk
  skillhost update --project nsdk --all

Behavior:
- no repo-name means update all repos in selected scope
- --all also means update all repos in selected scope
- repo-name means update one repo
- use git pull --ff-only
- do not merge
- do not rebase
- after update, automatically relink the selected scope when possible
- for project scope, relink only if current directory is a matching project checkout
- otherwise print:
  Updated project skill repo(s).
  Run inside the project checkout:
    skillhost relink --project <project>

11. remove

Examples:

  skillhost remove company-skills
  skillhost remove nsdk-skills --project nsdk

Behavior:
- requires repo-name
- does not support --all
- unlink SkillHost-managed symlinks for that repo where safely discoverable
- delete the cloned repo from ~/.skillhost
- remove repo entry from config
- do not remove unmanaged target skills
- do not remove user-owned directories

12. relink

Examples:

  skillhost relink
  skillhost relink company-skills
  skillhost relink --all
  skillhost relink --agent codex

  skillhost relink --project nsdk
  skillhost relink nsdk-skills --project nsdk
  skillhost relink --project nsdk --all
  skillhost relink --project nsdk --agent claude

Behavior:
- no repo-name means relink all repos in selected scope
- --all means relink all repos in selected scope
- repo-name means relink one repo
- --agent means relink only one registered agent
- user scope links into registered agents’ user_dir
- project scope links into registered agents’ project_dir under the current project root
- project relink must operate only on current Git repository root
- project relink must validate current git repo matches registered project remote
- do not scan disk
- skip unmanaged existing targets
- update SkillHost-managed symlinks when appropriate
- write/update .skillhost-links.json

13. unlink

Examples:

  skillhost unlink company-skills
  skillhost unlink --all
  skillhost unlink --agent codex --all

  skillhost unlink nsdk-skills --project nsdk
  skillhost unlink --project nsdk --all
  skillhost unlink --project nsdk --agent claude --all

Behavior:
- only remove manifest-managed symlinks
- never remove unmanaged directories
- never remove user-owned skills
- if no repo-name and no --all, refuse:
  Refusing to unlink all links implicitly. Use --all.
- --all unlinks all repos in selected scope
- project unlink only operates on current project root
- no full-disk cleanup

14. list / projects / agents / doctor / config

list:

  skillhost list
  skillhost list --project nsdk

Show repos and discovered skills in selected scope.

projects:

  skillhost projects

Show registered projects and normalized Git remotes.

agents:

  skillhost agents

Show registered agents and their user/project target directories.

doctor:

  skillhost doctor
  skillhost doctor --project nsdk

Check:
- config exists and is valid JSON
- git is available
- repos exist and are valid git repos
- skills are discoverable
- duplicate skill names
- agent target directories
- manifests
- broken symlinks
- missing sources
- current project matching status when --project is provided

config:

  skillhost config

Print absolute config path only.

15. Skill discovery

Given a cloned source repo:

Case A:
- repo root has SKILL.md
- repo itself is one skill

Case B:
- repo root has skills/*/SKILL.md
- each direct child under skills/ is one skill

Case C:
- repo root has */SKILL.md
- each direct child under repo root with SKILL.md is one skill
- ignore hidden dirs and obvious non-skill dirs:
  .git
  tests
  docs
  examples
  scripts
  references
  assets

Do not deep scan recursively beyond this.

Skill name:
- prefer name in YAML frontmatter of SKILL.md if present
- otherwise use directory name
- parser should be simple
- do not add PyYAML dependency

16. Git URL normalization

Normalize common Git URL forms:

  git@github.com:org/repo.git
  git@github.com:org/repo
  https://github.com/org/repo.git
  https://github.com/org/repo
  ssh://git@github.com/org/repo.git

All normalize to:

  github.com/org/repo

Support GitLab and other hosts similarly when possible.

Project matching:
- find current git root:
  git rev-parse --show-toplevel
- find origin URL:
  git remote get-url origin
- normalize it
- match against registered project remotes
- if --project is provided, validate current repo matches that project for relink/unlink
- if not matched, refuse project relink/unlink with clear message

17. Remove unsupported features

Remove from implementation, argparse, tests, docs:
- user subcommand
- project subcommand
- register-project
- config path
- config edit
- add --project-git
- --all-projects
- --all-skills
- --dry-run
- --force
- --include
- --exclude

Do not add these back.

18. Tests

Update existing tests and add tests for:

CLI:
- skillhost --help shows final commands
- skillhost config prints absolute path ending in ~/.skillhost/config.json
- no config path/edit commands exist
- no user/project subcommands exist
- no unsupported flags exist

Config:
- init creates config.json
- config.json contains version, home, agents, user_repos, projects
- built-in agents are initialized
- register/unregister project updates config
- register/unregister agent updates config

Git URL:
- normalize SSH scp-style GitHub URL
- normalize HTTPS GitHub URL
- normalize ssh:// GitHub URL
- strip .git

Discovery:
- single skill repo with root SKILL.md
- collection repo with skills/foo/SKILL.md
- flat collection repo with foo/SKILL.md
- no deep recursion

Linking:
- relink creates symlink and manifest
- relink skips unmanaged existing directory
- relink updates manifest-managed symlink
- duplicate skill names are reported/skipped
- unlink only removes manifest-managed symlinks
- unlink without repo and without --all refuses

Scope:
- add user repo writes user_repos
- add project repo requires registered project
- add project repo writes projects.<project>.repos
- update no repo updates all repos in selected scope
- remove requires repo name
- project relink validates current Git project

19. README update

Update README to document only the final command design.

Use this command table:

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

README examples:

User-level:

  skillhost add git@github.com:org/company-skills.git
  skillhost update
  skillhost relink
  skillhost remove company-skills

Project-level:

  skillhost register --project nsdk --git git@github.com:org/nsdk.git
  cd ~/code/nsdk
  skillhost add git@github.com:org/nsdk-skills.git --project nsdk
  skillhost update --project nsdk
  skillhost relink --project nsdk
  skillhost remove nsdk-skills --project nsdk

Agent registration:

  skillhost register --agent cursor --user-dir ~/.cursor/skills --project-dir .cursor/skills
  skillhost agents
  skillhost unregister --agent cursor

Config:

  skillhost config

Explain:
- this prints the absolute path to config.json
- config.json is the SSOT
- .skillhost-links.json is target-local link state

20. Quality bar

After refactor:
- run tests
- run package build if configured
- run `skillhost --help`
- run help for each command:
  skillhost register --help
  skillhost unregister --help
  skillhost add --help
  skillhost update --help
  skillhost remove --help
  skillhost relink --help
  skillhost unlink --help
  skillhost list --help
  skillhost projects --help
  skillhost agents --help
  skillhost doctor --help
  skillhost config --help

Do not implement features outside this specification.
Do not add extra CLI flags.
Do not create a new architecture if the existing one can be refactored.
Prefer the smallest coherent refactor that fully matches this final spec.