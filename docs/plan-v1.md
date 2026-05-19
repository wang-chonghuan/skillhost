You are building a public Python CLI tool named `skillhost`.

Goal:
Build a small, production-ready Python command-line tool that installs Agent Skills from Git repositories into local agent skill directories using symlinks.

The tool website is skillhost.dev.

Core philosophy:
- No registry.
- No server.
- No accounts.
- Git is the distribution system.
- Symlinks are the install system.
- Manifest files make unlink/remove safe.
- The tool must not execute any code from skill repositories.
- The tool must not overwrite user-owned existing skills.
- The tool must support both user-level shared skills and project-level skills.

Use a standard modern Python package structure:
- Python >= 3.10
- pyproject.toml
- src/ layout
- package name: skillhost
- CLI entry point: skillhost
- Use only Python standard library unless there is a very strong reason not to.
- Prefer argparse over external CLI frameworks to keep the package lightweight.
- Include pytest tests.
- Include a README.md.
- Include ruff-compatible formatting/linting config if useful.
- The package should be installable with:
  - pipx install .
  - uv tool install .
  - pip install .

Directory layout to create:

skillhost/
  pyproject.toml
  README.md
  src/
    skillhost/
      __init__.py
      cli.py
      config.py
      git_utils.py
      discovery.py
      linking.py
      agents.py
      projects.py
      paths.py
      errors.py
  tests/
    test_discovery.py
    test_git_utils.py
    test_linking.py
    test_projects.py

Persistent state directory:
- Default base directory: ~/.skillhost

Inside it:

~/.skillhost/
  config.toml
  user_repos/
    <repo-name>/
  project_repos/
    <project-name>/
      <repo-name>/
  state/
  locks/

The tool must create these directories as needed.

Use TOML for config.
Use Python 3.11 tomllib for reading TOML when available.
For writing TOML, avoid adding a dependency if possible. Implement a small controlled writer because the config schema is simple.

Config schema:

version = 1

[agents]
enabled = ["codex", "claude", "opencode"]

[user]
repos_dir = "~/.skillhost/user_repos"

[projects.<project-name>]
remotes = ["github.com/org/repo"]
repos_dir = "~/.skillhost/project_repos/<project-name>"

Agent target directories:

Codex:
- user target: ~/.agents/skills
- project target: .agents/skills

Claude Code:
- user target: ~/.claude/skills
- project target: .claude/skills

OpenCode:
- user target: ~/.config/opencode/skills
- project target: .opencode/skills

Important:
Use each agent's native target directory. Do not intentionally rely on one agent reading another agent's directory.

Main command tree:

skillhost
  user
    add <git-repo> [--name NAME] [--branch BRANCH]
    update [NAME]
    link [--agent codex|claude|opencode] [--dry-run]
    unlink [--agent codex|claude|opencode] [--dry-run]
    remove <name> [--force]
    list
    doctor

  project
    add <git-repo> --project PROJECT [--name NAME] [--branch BRANCH] [--project-git GIT_URL]
    register PROJECT --git GIT_URL
    update [PROJECT] [NAME]
    link [--project PROJECT] [--agent codex|claude|opencode] [--dry-run]
    unlink [--project PROJECT] [--agent codex|claude|opencode] [--dry-run]
    remove <name> --project PROJECT [--force]
    list [PROJECT]
    doctor [PROJECT]

Also support:
skillhost --version
skillhost --help

High-level command semantics:

1. skillhost user add <git-repo>
Clone a Git repository into ~/.skillhost/user_repos/<repo-name>.

If --name is not provided:
- Derive repo-name from the Git URL basename.
- Strip trailing .git.
- Example: git@github.com:acme/acme-skills.git -> acme-skills.

If the target clone path already exists:
- If it is a git repo with the same normalized origin URL, print that it already exists.
- If it conflicts, fail and ask the user to pass --name.

If --branch is provided:
- Clone that branch.

Do not link automatically unless you think it is extremely expected. Prefer not to link automatically. Tell user to run:
  skillhost user link

2. skillhost user update [NAME]
If NAME provided:
- Update only ~/.skillhost/user_repos/NAME.

If NAME omitted:
- Update all repos under ~/.skillhost/user_repos.

Update means:
- Validate repo is a Git repo.
- Run git pull --ff-only.
- Do not merge.
- Do not rebase.
- If dirty working tree exists, fail with a clear error.
- Use subprocess and show useful errors.

3. skillhost user link
Discover all skills from all repos under ~/.skillhost/user_repos.
Create symlinks into user-level target directories for enabled agents.

Default agents:
- codex
- claude
- opencode

If --agent is passed, link only for that agent.

Targets:
- codex: ~/.agents/skills
- claude: ~/.claude/skills
- opencode: ~/.config/opencode/skills

Conflict rule:
- If target path does not exist, create symlink.
- If target path is a symlink created by skillhost and recorded in manifest, and points to the same source, keep it.
- If target path is a symlink created by skillhost and recorded in manifest, and points to a different source from the same repo update, update it.
- If target path exists but is not recorded as skillhost-managed, skip and warn. Never overwrite user-owned skills by default.
- If two source repos provide the same skill name, skip that skill and report a conflict. Do not choose a winner.

Manifest:
For each target directory, create a JSON file:
  .skillhost-links.json

Example:
{
  "version": 1,
  "links": {
    "ng-git": {
      "source": "/Users/me/.skillhost/user_repos/narrative-skills/skills/ng-git",
      "scope": "user",
      "repo": "narrative-skills",
      "agent": "codex"
    }
  }
}

Only unlink/remove symlinks recorded in manifest.

4. skillhost user unlink
Remove only symlinks that were previously created by skillhost for user-level targets.
Do not delete any target that is not listed in .skillhost-links.json.
Do not delete real directories.
Clean manifest entries after unlinking.
If --agent is passed, unlink only for that agent.

5. skillhost user remove <name>
Remove a user-level source repo.

Before deleting the clone:
- Unlink all symlinks created from that repo.
- If repo has dirty working tree, refuse unless --force.
- Then delete ~/.skillhost/user_repos/<name>.

6. skillhost user list
Show:
- Registered user repos.
- Discovered skills per repo.
- Link status per agent if easy.
Keep output readable.

7. skillhost user doctor
Check:
- ~/.skillhost exists.
- user_repos exists.
- git is available.
- each user repo is a valid git repo.
- each repo has valid skills.
- each agent target dir status.
- broken symlinks.
- manifest entries pointing to missing sources.
- name conflicts.
Return non-zero if serious issues exist.

Project-level behavior:

Project-level skills are different from user-level skills.
They are linked into the current project's local agent directories:
- .agents/skills
- .claude/skills
- .opencode/skills

No full-disk search.
No automatic search across all checkouts.
`skillhost project link` operates on the current Git repository root only.

Project identification:
- To link project skills, determine the current git repository root by running:
  git rev-parse --show-toplevel
- Determine the current repo's remote URL from:
  git remote get-url origin
- Normalize the URL.
- Match normalized URL against configured project remotes.
- If --project PROJECT is provided, use that project explicitly but still validate current repo unless project has no remotes configured.
- If no matching project can be found, print a clear error:
  "Current directory is not a registered project. Run: skillhost project register <name> --git <repo-url>"

URL normalization:
Implement a helper that converts common Git URL formats to a canonical string:
- git@github.com:org/repo.git
- git@github.com:org/repo
- https://github.com/org/repo.git
- https://github.com/org/repo
- ssh://git@github.com/org/repo.git

All should normalize to:
  github.com/org/repo

Support GitLab and other hosts similarly:
  host/org/repo

Do not overcomplicate. Implement robust handling for common SSH and HTTPS forms.

Project config:

skillhost project register PROJECT --git GIT_URL
- Normalize GIT_URL.
- Add it to [projects.PROJECT].remotes in config.
- Create repos_dir default:
  ~/.skillhost/project_repos/PROJECT

skillhost project add <git-repo> --project PROJECT [--project-git GIT_URL]
- If PROJECT is not registered and --project-git provided:
  register project first.
- If PROJECT is not registered and --project-git not provided:
  error and ask user to run project register or pass --project-git.
- Clone the skill repo into:
  ~/.skillhost/project_repos/PROJECT/<repo-name>

skillhost project update [PROJECT] [NAME]
- If PROJECT omitted, update all project repos.
- If PROJECT provided, update all repos for that project.
- If NAME provided, update only that repo within that project.
- Same git update rules as user update.

skillhost project link [--project PROJECT]
- Determine current repo root.
- Determine project by normalized origin URL unless --project is provided.
- Discover skills from:
  ~/.skillhost/project_repos/<project-name>/*
- Link them into current repo root:
  <repo-root>/.agents/skills
  <repo-root>/.claude/skills
  <repo-root>/.opencode/skills
- Same conflict rules:
  - Never overwrite user-owned existing skill.
  - If target exists and is not skillhost-managed, skip.
  - If duplicate skill names across project source repos, skip and report conflict.
- Write manifests in each target dir:
  .skillhost-links.json

skillhost project unlink [--project PROJECT]
- Determine current repo root.
- Remove only skillhost-managed symlinks for that project from current repo's agent target dirs.
- Do not touch user-owned skills.
- Clean manifest.

skillhost project remove <name> --project PROJECT
- Unlink symlinks created from that project repo if current repo matches. Since remove may be run outside a project checkout, unlink only where manifest data can safely locate known linked targets if implemented; otherwise tell the user to run project unlink in the project repo first.
- Refuse to delete dirty repo unless --force.
- Delete:
  ~/.skillhost/project_repos/PROJECT/<name>

skillhost project list [PROJECT]
Show projects, registered remotes, project skill repos, discovered skills.

skillhost project doctor [PROJECT]
Check project config, remotes, skill repos, conflicts, and current directory matching status.

Skill discovery rules:

Given a cloned source repo path:

Case A: repo root has SKILL.md
- The repo itself is one skill.
- Skill source path = repo root.
- Skill name:
  - Prefer name from SKILL.md YAML frontmatter if present.
  - Otherwise use repo directory name.

Case B: repo root has skills/*/SKILL.md
- Each direct child under skills/ with SKILL.md is a skill.
- Skill source path = skills/<name>
- Skill name:
  - Prefer frontmatter name.
  - Otherwise use directory name.

Case C: repo root has */SKILL.md
- Each direct child under repo root with SKILL.md is a skill.
- Exclude hidden dirs, .git, tests, docs, examples, scripts, references, assets.
- Skill name:
  - Prefer frontmatter name.
  - Otherwise use directory name.

Do not deep recursive scan beyond this.
Do not scan references, assets, examples recursively.
A skill is valid if and only if it has SKILL.md.

Frontmatter parser:
- SKILL.md may start with YAML frontmatter:
  ---
  name: ng-git
  description: ...
  ---
- Implement a simple parser to read name and description.
- Do not depend on PyYAML.
- Support simple "key: value" pairs only.
- If no frontmatter, fallback to directory name.
- Validate skill name:
  - lowercase letters, digits, hyphen only
  - must not be empty
- Warn if directory name and frontmatter name differ, but still use frontmatter name.

Symlink behavior:
- Use absolute resolved source paths for symlink targets.
- On Unix/macOS, create directory symlinks.
- On Windows, attempt symlink. If it fails because privileges are missing, print a clear error explaining that Windows symlink support may require Developer Mode or administrator privileges.
- Do not silently copy directories.

Dry run:
- link and unlink should support --dry-run.
- Print what would be created, skipped, removed.

Exit codes:
- 0 success
- 1 user error / validation error / conflicts
- 2 git command failure
- 3 unexpected internal error

Errors should be clear and actionable.

Implementation detail suggestions:

files:

paths.py:
- expand_path
- skillhost_home
- config_path
- user_repos_dir
- project_repos_dir(project)
- agent target path helpers

agents.py:
- Agent dataclass:
  name
  user_target
  project_target
- get_agents(names: list[str] | None)

git_utils.py:
- run_git(args, cwd=None)
- clone_repo(url, dest, branch=None)
- pull_ff_only(repo)
- is_git_repo(path)
- is_dirty(repo)
- get_origin_url(repo)
- get_repo_root(path)
- normalize_git_url(url)

discovery.py:
- Skill dataclass:
  name
  source_path
  repo_name
  scope
  project
  description
- discover_skills_in_repo(repo_path, repo_name, scope, project=None)
- discover_user_skills()
- discover_project_skills(project)

linking.py:
- load_manifest(target_dir)
- save_manifest(target_dir, manifest)
- link_skills(skills, targets, scope, project=None, dry_run=False)
- unlink_scope(targets, scope, project=None, repo_name=None, dry_run=False)
- conflict detection
- safe symlink handling

config.py:
- load_config()
- save_config()
- ensure_default_config()
- register_project(project, git_url)
- get_project_by_remote(normalized_remote)
- list_projects()

cli.py:
- argparse command tree.
- Call functions above.
- Handle exceptions and exit codes.

Testing:
Write pytest tests for:
1. normalize_git_url:
- git@github.com:org/repo.git -> github.com/org/repo
- https://github.com/org/repo.git -> github.com/org/repo
- ssh://git@github.com/org/repo.git -> github.com/org/repo

2. skill discovery:
- single skill repo with SKILL.md
- collection repo with skills/foo/SKILL.md
- flat collection repo with foo/SKILL.md
- no deep recursion

3. frontmatter:
- extracts name and description
- falls back to dir name

4. linking:
- creates symlink
- does not overwrite existing real directory
- updates skillhost-managed link
- detects duplicate skill names
- unlink only removes manifest-managed symlinks

5. project matching:
- register project remote
- detect current repo remote
- match normalized URL

README should include:

Title:
Skillhost

Tagline:
Install Agent Skills from Git repos into Codex, Claude Code, and OpenCode using symlinks.

Explain:
- Git is the distribution system.
- Symlinks are the install system.
- No registry, no server, no account.

Install:
pipx install skillhost
uv tool install skillhost

User-level example:
skillhost user add git@github.com:your-org/company-skills.git
skillhost user update
skillhost user link
skillhost user list
skillhost user doctor

Project-level example:
cd ~/code/my-project
skillhost project register my-project --git git@github.com:your-org/my-project.git
skillhost project add git@github.com:your-org/my-project-skills.git --project my-project
skillhost project link

Explain target dirs:
User:
- Codex: ~/.agents/skills
- Claude Code: ~/.claude/skills
- OpenCode: ~/.config/opencode/skills

Project:
- Codex: .agents/skills
- Claude Code: .claude/skills
- OpenCode: .opencode/skills

Explain repo layout:
Single skill repo:
my-skill/
  SKILL.md

Skill collection repo:
company-skills/
  skills/
    git/
      SKILL.md
    db/
      SKILL.md

Flat collection repo:
company-skills/
  git/
    SKILL.md
  db/
    SKILL.md

Conflict policy:
- Existing user-owned skills are never overwritten.
- Duplicate skill names across source repos are skipped and reported.
- `unlink` only removes skillhost-managed symlinks.

Security:
- skillhost never executes code from skill repos.
- skillhost only clones, updates, discovers SKILL.md files, and creates/removes symlinks.

Important product decisions:
- Do not implement registry support.
- Do not implement semver.
- Do not implement package resolution.
- Do not implement full-disk project discovery.
- Do not auto-run skill scripts.
- Do not overwrite non-managed target directories.
- Keep v1 narrow and reliable.

Implement incrementally. First generate the package skeleton and core tests, then implement modules until tests pass. Prefer simple readable code over clever abstractions.