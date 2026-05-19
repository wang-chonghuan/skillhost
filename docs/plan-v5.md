# Skillhost v5 Plan: Interactive add/link flow and explicit update repo selectors

## Objective

Improve Skillhost's default user experience for adding and updating skill repositories.

New behavior:

1. After `skillhost add <git-repo>` successfully clones or registers a user-level skill repository, Skillhost should automatically start an interactive prompt that lets the user choose where to link the discovered skills.
2. The interactive link prompt should support built-in user-level agent targets and custom target directories.
3. `skillhost update` should support explicit repo selection flags:
   - `--user_repos XXX`
   - `--project_repos YYY`
4. If `skillhost update` is called without repo selector flags, it should update all known repos by default.
5. After `skillhost update` completes, Skillhost should ask whether to automatically link the updated skills: `Y` or `N`.
6. Existing `--agent` behavior must be preserved for non-interactive and scriptable use.

This plan builds on the v2 command shape where user-level commands are top-level commands:

```sh
skillhost add <git-repo> [--name NAME] [--branch BRANCH]
skillhost update [--user_repos NAME] [--project_repos SELECTOR]
skillhost link [--agent codex|claude|opencode] [--target-dir PATH] [--dry-run]
skillhost unlink [--agent codex|claude|opencode] [--target-dir PATH] [--dry-run]
skillhost remove <name> [--force]
skillhost list
skillhost doctor
```

Project-level commands remain available under `skillhost project ...`.

## Product decisions

- `skillhost add` remains a user-level operation.
- `skillhost add` should not silently link after cloning. It should ask the user interactively.
- The interactive prompt is the default when stdout/stdin are TTYs.
- `--agent` must remain supported and should allow non-interactive linking to a known agent target.
- Automation must remain possible. Add flags to skip prompts where needed.
- Custom directories are first-class link targets, not hacks.
- Manifest tracking must still make unlink/remove safe for all targets, including custom target directories.
- Skillhost must never overwrite user-owned existing skills.
- Skillhost must never execute code from skill repositories.

## Command behavior summary

### `skillhost add`

New form:

```sh
skillhost add <git-repo> [--name NAME] [--branch BRANCH] [--agent codex|claude|opencode] [--target-dir PATH] [--no-link-prompt] [--yes]
```

Behavior:

1. Clone the Git repo into the user-level repos directory:

```text
~/.skillhost/user_repos/<repo-name>
```

2. Discover valid skills by looking for `SKILL.md`.
3. If no skills are found, print a clear message and do not prompt to link.
4. If skills are found:
   - If `--agent` is provided, link to that agent's user-level default skill directory without asking for agent choice.
   - If `--target-dir PATH` is provided, link to that custom directory without asking for target choice.
   - If neither `--agent` nor `--target-dir` is provided and the command is running in an interactive terminal, ask the user where to link.
   - If running non-interactively, print the next suggested commands and do not block waiting for input.

Interactive prompt options after add:

```text
Link discovered skills now?
  1. Codex user skills      ~/.agents/skills
  2. Claude Code user skills ~/.claude/skills
  3. OpenCode user skills   ~/.config/opencode/skills
  4. All supported agents
  5. Custom directory
  6. Skip linking
Choose [1-6]:
```

If the user chooses `Custom directory`, ask:

```text
Custom skill target directory:
```

Then create symlinks for all discovered skills into that directory.

Default recommendation:

- If the user presses Enter without choosing, default to `Skip linking` unless `--yes` is provided.
- If `--yes` is provided with `--agent`, link to the selected agent without further prompts.
- If `--yes` is provided without `--agent` or `--target-dir`, choose `All supported agents` only if this behavior is explicitly documented in help text. Otherwise fail with a clear message asking for `--agent`, `--target-dir`, or interactive mode.

### `skillhost link`

Existing behavior remains supported:

```sh
skillhost link --agent codex
skillhost link --agent claude
skillhost link --agent opencode
skillhost link --dry-run
```

Add custom target support:

```sh
skillhost link --target-dir ~/.agents/skills
skillhost link --target-dir /path/to/custom/skills
```

Rules:

- `--agent` and `--target-dir` are mutually exclusive unless there is a strong reason to allow both.
- `--agent codex` links to the Codex user-level default target:

```text
~/.agents/skills
```

- `--agent claude` links to:

```text
~/.claude/skills
```

- `--agent opencode` links to:

```text
~/.config/opencode/skills
```

- `--target-dir PATH` links to the exact custom directory.
- Custom target directories must also get `.skillhost-links.json` manifests.

### `skillhost update`

New form:

```sh
skillhost update [--user_repos NAME] [--project_repos SELECTOR] [--agent codex|claude|opencode] [--target-dir PATH] [--no-link-prompt] [--yes]
```

Default behavior:

```sh
skillhost update
```

Updates all known repos by default:

- all user repos under `~/.skillhost/user_repos/`
- all project repos under `~/.skillhost/project_repos/`

Selector behavior:

```sh
skillhost update --user_repos nskills
```

Updates only:

```text
~/.skillhost/user_repos/nskills
```

```sh
skillhost update --project_repos my-project/project-skills
```

Updates only:

```text
~/.skillhost/project_repos/my-project/project-skills
```

Also support selecting all explicitly:

```sh
skillhost update --user_repos all
skillhost update --project_repos all
skillhost update --user_repos all --project_repos all
```

If both selectors are omitted, behavior is equivalent to:

```sh
skillhost update --user_repos all --project_repos all
```

After update completes, prompt:

```text
Update complete. Link updated skills now? [Y/n]:
```

- `Y` links updated repos using the selected target behavior.
- `N` exits after printing next suggested link commands.
- Pressing Enter defaults to `Y` for interactive terminals.
- In non-interactive mode, do not prompt. Print next suggested link commands instead unless `--yes` is provided.

If `--agent` is provided:

```sh
skillhost update --user_repos nskills --agent codex
```

Then after update:

- In interactive mode: ask `Link updated skills to Codex now? [Y/n]:`.
- With `--yes`: update and link to Codex without prompting.

If `--target-dir` is provided:

```sh
skillhost update --user_repos nskills --target-dir /path/to/skills
```

Then after update:

- In interactive mode: ask `Link updated skills to /path/to/skills now? [Y/n]:`.
- With `--yes`: update and link to the custom target without prompting.

## Naming and argparse details

The user requested these exact flags:

```sh
--user_repos XXX
--project_repos YYY
```

Implement those exact spellings.

Optional convenience aliases may be added only if tests cover that the requested spellings still work:

```sh
--user-repos XXX
--project-repos YYY
```

If aliases are added, help text should show the canonical requested names first.

`--user_repos` accepts:

- a repo name, for example `nskills`
- `all`

`--project_repos` accepts:

- `PROJECT/REPO`, for example `my-project/project-skills`
- `all`

Do not make `--project_repos project-skills` ambiguous across projects. If a shorthand is later desired, it should be a separate plan.

Mutual exclusion:

- `--agent` and `--target-dir` should be mutually exclusive.
- `--no-link-prompt` and `--yes` should be allowed together, but `--no-link-prompt` wins and prevents automatic linking.

## Link target model

Add an internal link target abstraction:

```text
LinkTarget
  kind: agent | custom
  agent: codex | claude | opencode | null
  scope: user | project | custom
  path: absolute path
  label: human readable label
```

Built-in user-level targets:

```text
Codex:       ~/.agents/skills
Claude Code: ~/.claude/skills
OpenCode:    ~/.config/opencode/skills
```

Built-in project-level targets remain:

```text
Codex:       .agents/skills
Claude Code: .claude/skills
OpenCode:    .opencode/skills
```

Custom targets:

- Must be expanded with `~` support.
- Should be resolved to an absolute path before writing manifests.
- Should be created if missing.
- Should be protected by the same conflict policy as built-in targets.

## Manifest changes

Existing manifest format should remain compatible.

For custom targets, add enough metadata to identify the target:

```json
{
  "version": 1,
  "links": {
    "ng-git": {
      "source": "/Users/me/.skillhost/user_repos/narrative-skills/skills/ng-git",
      "scope": "user",
      "repo": "narrative-skills",
      "agent": null,
      "target_kind": "custom"
    }
  }
}
```

For built-in agent targets, keep `agent` populated:

```json
{
  "version": 1,
  "links": {
    "ng-git": {
      "source": "/Users/me/.skillhost/user_repos/narrative-skills/skills/ng-git",
      "scope": "user",
      "repo": "narrative-skills",
      "agent": "codex",
      "target_kind": "agent"
    }
  }
}
```

Backward compatibility:

- Existing manifests without `target_kind` should still be readable.
- If `target_kind` is missing and `agent` is present, treat it as `target_kind = "agent"`.
- If both are missing, treat it cautiously and never delete non-symlink directories.

## Interactive prompting requirements

Use only Python standard library.

Do not add an external prompt framework.

Implement simple helpers:

```text
is_interactive()
prompt_choice(message, options, default=None)
prompt_yes_no(message, default=True)
prompt_path(message)
```

Rules:

- Only prompt if both stdin and stdout are TTYs.
- Never prompt in CI/non-interactive mode.
- All prompts must have clear escape paths.
- `Ctrl+C` should exit cleanly with a short message.
- Invalid choices should be re-prompted with a clear error.
- `--yes` should never cause unsafe overwrites.
- `--yes` only answers Skillhost's own confirmation prompts.

## Detailed implementation plan

### 1. Update CLI parser

Modify `src/skillhost/cli.py`.

For `skillhost add`, add:

```text
--agent codex|claude|opencode
--target-dir PATH
--no-link-prompt
--yes
```

For `skillhost update`, replace or extend the old positional `NAME` behavior with:

```text
--user_repos NAME_OR_ALL
--project_repos PROJECT_REPO_OR_ALL
--agent codex|claude|opencode
--target-dir PATH
--no-link-prompt
--yes
```

Preserve existing `skillhost link --agent ...` behavior and add:

```text
--target-dir PATH
```

### 2. Add prompt helpers

Create or update a module such as:

```text
src/skillhost/prompts.py
```

Responsibilities:

- Detect interactive mode.
- Ask numbered choices.
- Ask yes/no questions.
- Read custom target directories.
- Return structured results, not raw strings where possible.

### 3. Add link target helpers

Create or update a module such as:

```text
src/skillhost/targets.py
```

Responsibilities:

- Convert `--agent` to the correct user-level or project-level target path.
- Convert `--target-dir` to an absolute custom path.
- Build interactive target options for `skillhost add`.
- Validate mutually exclusive target options.

### 4. Update add flow

In the add command handler:

1. Clone or reuse the repo as today.
2. Discover skills in the added repo.
3. Print discovered skill count and names.
4. Determine link target behavior:
   - explicit `--agent`
   - explicit `--target-dir`
   - interactive prompt
   - no prompt/non-interactive fallback
5. Link selected target(s) using the existing safe linking logic.
6. Write manifests.
7. Print a concise summary.

Example output:

```text
Added nskills from git@github.com:your-org/nskills.git
Discovered 10 skills.

Link discovered skills now?
  1. Codex user skills       ~/.agents/skills
  2. Claude Code user skills ~/.claude/skills
  3. OpenCode user skills    ~/.config/opencode/skills
  4. All supported agents
  5. Custom directory
  6. Skip linking
Choose [1-6]: 1

Linked 10 skills to Codex user skills: ~/.agents/skills
```

### 5. Update update flow

In the update command handler:

1. Resolve selected repos:
   - no selectors means all user and all project repos
   - `--user_repos NAME` means one user repo
   - `--user_repos all` means all user repos
   - `--project_repos PROJECT/REPO` means one project repo
   - `--project_repos all` means all project repos
2. Run `git pull --ff-only` for each selected repo.
3. Refuse dirty repos as before.
4. Print update summary.
5. Ask whether to link updated skills:
   - interactive yes/no prompt
   - `--yes` means yes
   - `--no-link-prompt` means no
   - non-interactive without `--yes` means no prompt and print suggested commands
6. If linking is accepted, link only skills from updated repos where feasible.
   - If the existing linking code only links all repos, refactor it to accept an optional repo filter.
   - Do not regress current full-link behavior.

Example:

```text
Updated 1 user repo: nskills
Link updated skills now? [Y/n]: y
Linked 10 skills to Codex user skills: ~/.agents/skills
```

If no explicit target was provided during update and user answers `Y`, ask for target choice using the same options as add.

### 6. Preserve and extend `--agent`

The `--agent` parameter remains the preferred non-interactive way to link to a known agent target.

Examples:

```sh
skillhost add git@github.com:your-org/nskills.git --agent codex --yes
skillhost update --user_repos nskills --agent codex --yes
skillhost link --agent codex
```

Expected behavior:

- No interactive target selection is needed when `--agent` is present.
- Conflict policy remains unchanged.
- Only the selected agent target is modified.

### 7. Add custom directory support

Examples:

```sh
skillhost add git@github.com:your-org/nskills.git --target-dir ~/.agents/skills --yes
skillhost link --target-dir /tmp/codex-skills
skillhost update --user_repos nskills --target-dir ~/custom-skills --yes
```

Requirements:

- Expand `~`.
- Create the target directory if missing.
- Add or update `.skillhost-links.json` inside the target directory.
- Never delete or overwrite non-Skillhost files.

### 8. Update docs and README

Update:

- `README.md`
- CLI help examples if present
- Any docs that describe add/update/link behavior
- Frontend copy only if it currently claims `add` never prompts or if command examples become outdated

README should include examples:

```sh
skillhost add git@github.com:your-org/nskills.git
```

Then explain that Skillhost asks where to link:

```text
Codex user skills: ~/.agents/skills
Claude Code user skills: ~/.claude/skills
OpenCode user skills: ~/.config/opencode/skills
Custom directory
Skip linking
```

Update examples:

```sh
skillhost update
skillhost update --user_repos nskills
skillhost update --project_repos my-project/project-skills
skillhost update --user_repos nskills --agent codex --yes
```

## Tests

Add or update tests under the Python test suite.

Recommended test files:

```text
tests/test_cli_add_interactive.py
tests/test_cli_update_selectors.py
tests/test_custom_targets.py
tests/test_prompts.py
```

### Required acceptance coverage

1. `skillhost add <repo>` in interactive mode prompts for link target after discovering skills.
2. Choosing Codex creates symlinks under `~/.agents/skills`.
3. Choosing Claude Code creates symlinks under `~/.claude/skills`.
4. Choosing OpenCode creates symlinks under `~/.config/opencode/skills`.
5. Choosing All links to all three built-in user-level targets.
6. Choosing Custom directory links to the provided custom path.
7. Choosing Skip does not link.
8. Non-interactive `skillhost add <repo>` does not hang waiting for input.
9. `skillhost add <repo> --agent codex --yes` links to Codex without prompting.
10. `skillhost add <repo> --target-dir PATH --yes` links to the custom target without prompting.
11. `skillhost update` with no selectors updates all user and project repos.
12. `skillhost update --user_repos nskills` updates only the selected user repo.
13. `skillhost update --project_repos my-project/project-skills` updates only the selected project repo.
14. `skillhost update --user_repos all` updates all user repos.
15. `skillhost update --project_repos all` updates all project repos.
16. After interactive update, answering `Y` triggers linking.
17. After interactive update, answering `N` does not link.
18. `skillhost update --user_repos nskills --agent codex --yes` updates and links to Codex without prompting.
19. `--agent` and `--target-dir` cannot be used together.
20. Custom target manifests are written and later unlink/remove only affect Skillhost-managed symlinks.
21. Existing user-owned files/directories in custom target directories are never overwritten.
22. Existing manifests without `target_kind` remain readable.

## Backward compatibility

- Keep existing `skillhost link --agent ...` behavior.
- Keep existing project-level commands.
- Do not remove safe manifest behavior.
- Do not remove existing config locations.
- The old positional `skillhost update NAME` may be removed or kept as a compatibility alias, but the new documented behavior should prefer `--user_repos NAME`.
- If the positional form is kept, tests must make sure it does not conflict with the no-argument "update all repos" default.

## Error handling

- If `--user_repos NAME` does not exist, fail with a clear error and list available user repos.
- If `--project_repos PROJECT/REPO` does not exist, fail with a clear error and list available project repos.
- If a repo is dirty, skip or fail consistently with existing update behavior. Prefer fail-fast unless current behavior is skip-and-report.
- If no repos exist and `skillhost update` is run, print `No repositories configured.` and exit successfully.
- If link target selection is invalid, re-prompt in interactive mode or fail in non-interactive mode.
- If a custom target path cannot be created, fail with the OS error and do not partially write manifests.

## Security and safety requirements

- Never execute code from skill repositories.
- Never overwrite user-owned skills.
- Never remove paths not recorded in `.skillhost-links.json`.
- Never remove real directories during unlink.
- Do not let `--yes` bypass conflict protection.
- Keep `git pull --ff-only` for updates.
- Keep dirty repo protections.

## Example final UX

### Add and link to Codex interactively

```sh
skillhost add git@github.com:your-org/nskills.git
```

```text
Added nskills.
Discovered 10 skills.

Link discovered skills now?
  1. Codex user skills       ~/.agents/skills
  2. Claude Code user skills ~/.claude/skills
  3. OpenCode user skills    ~/.config/opencode/skills
  4. All supported agents
  5. Custom directory
  6. Skip linking
Choose [1-6]: 1

Linked 10 skills to Codex user skills.
```

### Add and link to Codex non-interactively

```sh
skillhost add git@github.com:your-org/nskills.git --agent codex --yes
```

### Add and link to a custom directory

```sh
skillhost add git@github.com:your-org/nskills.git --target-dir ~/my-codex-skills --yes
```

### Update all repos, then choose whether to link

```sh
skillhost update
```

```text
Updated user repos: nskills, company-skills
Updated project repos: my-project/project-skills

Link updated skills now? [Y/n]: y
```

### Update one user repo

```sh
skillhost update --user_repos nskills
```

### Update one project repo

```sh
skillhost update --project_repos my-project/project-skills
```

### Update one user repo and link to Codex without prompts

```sh
skillhost update --user_repos nskills --agent codex --yes
```
