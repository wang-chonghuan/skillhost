# Skillhost v2 Plan: Promote user-level commands to top-level commands

## Objective

Change the CLI command shape so user-level commands no longer require the `user` namespace.

Current v1 user-level form:

```sh
skillhost user add <git-repo>
skillhost user update [NAME]
skillhost user link [--agent codex|claude|opencode] [--dry-run]
skillhost user unlink [--agent codex|claude|opencode] [--dry-run]
skillhost user remove <name> [--force]
skillhost user list
skillhost user doctor
```

New v2 user-level form:

```sh
skillhost add <git-repo> [--name NAME] [--branch BRANCH]
skillhost update [NAME]
skillhost link [--agent codex|claude|opencode] [--dry-run]
skillhost unlink [--agent codex|claude|opencode] [--dry-run]
skillhost remove <name> [--force]
skillhost list
skillhost doctor
```

Project-level commands stay namespaced:

```sh
skillhost project add <git-repo> --project PROJECT [--name NAME] [--branch BRANCH] [--project-git GIT_URL]
skillhost project register PROJECT --git GIT_URL
skillhost project update [PROJECT] [NAME]
skillhost project link [--project PROJECT] [--agent codex|claude|opencode] [--dry-run]
skillhost project unlink [--project PROJECT] [--agent codex|claude|opencode] [--dry-run]
skillhost project remove <name> --project PROJECT [--force]
skillhost project list [PROJECT]
skillhost project doctor [PROJECT]
```

The old `skillhost user ...` command format must be removed, not kept as an alias.

## Product decisions

- `skillhost add`, `update`, `link`, `unlink`, `remove`, `list`, and `doctor` mean user-level operations.
- `skillhost project ...` remains the only project-level namespace.
- Do not support `skillhost user ...` for compatibility in v2.
- Do not add a deprecation warning for `skillhost user ...`; it should fail through argparse as an invalid command.
- Keep storage, config schema, manifest schema, and implementation semantics unchanged unless needed for command routing.
- Keep internal function names such as `user_add` if useful; the public CLI shape is what changes.
- Update every user-facing mention in docs, README, frontend copy, and tests.

## Files to modify

### CLI implementation

- `src/skillhost/cli.py`

### Python tests

- Existing tests may not currently assert command-tree shape; add or update tests to cover it.
- Candidate new test file:
  - `tests/test_cli.py`

### Documentation

- `README.md`
- `docs/plan-v1.md` should remain historical and does not need to be rewritten.
- `docs/plan-web-v1.md` is historical, but it contains frontend copy requirements with old commands. Prefer adding v2 notes only if tests or docs validation refer to it. Do not treat it as the source of truth after this plan.
- `docs/plan-v2.md` is this implementation plan.

### Frontend copy

Update all command examples and text under:

- `web/frontend/src/components/Hero.tsx`
- `web/frontend/src/components/Workflow.tsx`
- Any other `web/frontend/src/**/*.tsx` file containing `skillhost user` or references to the old user-level command shape.

### Frontend acceptance tests

- `tests/web/test_skillhost_frontend.py`

## Detailed implementation plan

### 1. Update CLI parser shape

In `src/skillhost/cli.py`, change `build_parser()` from this top-level structure:

```text
skillhost
  user
    add
    update
    link
    unlink
    remove
    list
    doctor
  project
    add
    register
    update
    link
    unlink
    remove
    list
    doctor
```

to this structure:

```text
skillhost
  add
  update
  link
  unlink
  remove
  list
  doctor
  project
    add
    register
    update
    link
    unlink
    remove
    list
    doctor
```

Implementation notes:

- Keep `parser.add_argument("--version", ...)` unchanged.
- The root subparser should contain the user-level commands directly.
- Remove the `user = sub.add_parser("user")` parser and its nested subparser.
- Attach existing handlers directly:
  - root `add` -> `user_add`
  - root `update` -> `user_update`
  - root `link` -> `user_link`
  - root `unlink` -> `user_unlink`
  - root `remove` -> `user_remove`
  - root `list` -> `user_list`
  - root `doctor` -> `user_doctor`
- Keep `project = sub.add_parser("project")` and all project subcommands unchanged.
- Ensure no top-level parser accepts `user` as a command.

Expected behavior after the parser change:

```sh
skillhost add --help
skillhost update --help
skillhost link --help
skillhost unlink --help
skillhost remove --help
skillhost list --help
skillhost doctor --help
skillhost project add --help
```

must work.

This command must fail:

```sh
skillhost user add --help
```

Argparse exit code for invalid command is expected to be `2`.

### 2. Update CLI output and command suggestions

Search all Python source for old command strings:

```sh
grep -R "skillhost user" -n src tests README.md docs web/frontend
```

Update actionable suggestions in `src/skillhost/cli.py`:

- In `user_add`, change:

```text
Run: skillhost user link
```

to:

```text
Run: skillhost link
```

- Any other error/help/action text that says `skillhost user ...` must be changed to the new top-level form.
- Do not change project suggestions such as `skillhost project register ...`.

### 3. Add CLI command-shape tests

Add `tests/test_cli.py` with direct parser or `main()` coverage.

Recommended tests:

1. `skillhost --version` still works.
2. Top-level user command help works:
   - `main(["add", "--help"])` raises `SystemExit(0)` or subprocess exits `0`.
   - `main(["link", "--help"])` raises `SystemExit(0)` or subprocess exits `0`.
3. Old user namespace is rejected:
   - `main(["user", "add", "--help"])` raises `SystemExit(2)`.
4. Project namespace still works:
   - `main(["project", "add", "--help"])` raises `SystemExit(0)`.
5. Parser command list does not include `user` and does include all new top-level user commands.

Keep tests isolated from real home directories. For tests that execute behavior instead of help parsing, set `SKILLHOST_HOME` to a temp directory. Help-only parser tests do not need to touch state.

### 4. Update README

Update `README.md` user-level examples.

Old:

```sh
skillhost user add git@github.com:your-org/company-skills.git
skillhost user update
skillhost user link
skillhost user list
skillhost user doctor
```

New:

```sh
skillhost add git@github.com:your-org/company-skills.git
skillhost update
skillhost link
skillhost list
skillhost doctor
```

Old:

```sh
skillhost user link --agent codex
skillhost user unlink --agent claude --dry-run
```

New:

```sh
skillhost link --agent codex
skillhost unlink --agent claude --dry-run
```

Also update surrounding prose:

- `By default skillhost user link...` -> `By default skillhost link...`
- If README mentions `skillhost user remove`, change to `skillhost remove`.
- Keep project examples unchanged.

### 5. Update frontend copy

Update command examples in `web/frontend/src/components/Hero.tsx`.

Old:

```sh
$ skillhost user add git@github.com:acme/acme-skills.git
$ skillhost user link
```

New:

```sh
$ skillhost add git@github.com:acme/acme-skills.git
$ skillhost link
```

Update command examples in `web/frontend/src/components/Workflow.tsx`.

Old user workflow examples:

```sh
skillhost user add git@github.com:your-org/company-skills.git
skillhost user update
skillhost user link
skillhost user unlink
skillhost user remove company-skills
```

New user workflow examples:

```sh
skillhost add git@github.com:your-org/company-skills.git
skillhost update
skillhost link
skillhost unlink
skillhost remove company-skills
```

Keep project workflow examples unchanged:

```sh
skillhost project register ...
skillhost project add ...
skillhost project link
skillhost project unlink
skillhost project remove ...
```

After edits, run:

```sh
grep -R "skillhost user" -n web/frontend/src
```

It should return no matches.

### 6. Update frontend acceptance tests

In `tests/web/test_skillhost_frontend.py`, update expected strings.

Old expected command:

```python
"skillhost user add git@github.com:your-org/company-skills.git"
```

New expected command:

```python
"skillhost add git@github.com:your-org/company-skills.git"
```

Add negative assertion if useful:

```python
self.assertNotIn("skillhost user ", combined)
```

This ensures frontend copy does not regress to the old command form.

### 7. Update or add Python acceptance tests for command text

Add or update tests to ensure Python source output no longer suggests the old form.

Possible test:

```python
def test_user_add_suggests_top_level_link(tmp_path, monkeypatch, capsys):
    # Use a local git repo fixture as the source repo.
    # Set SKILLHOST_HOME to tmp_path / "home".
    # Run main(["add", str(source_repo)])
    # Assert stdout contains "Run: skillhost link".
    # Assert stdout does not contain "skillhost user".
```

This is optional if parser-shape tests and grep checks are part of verification, but it is valuable because it covers user-visible CLI output.

### 8. Update docs and plans

`docs/plan-v2.md` should be committed as the v2 source-of-truth plan.

Do not rewrite `docs/plan-v1.md`; it documents v1 requirements and should remain historical.

For `docs/plan-web-v1.md`:

- It is also historical, but it contains old command text.
- If the repository policy is that old plan docs remain immutable, leave it unchanged.
- If the project wants `grep -R "skillhost user"` to return no matches anywhere except historical docs, add a short note at the top saying v2 command examples supersede v1 examples, but do not rewrite the entire file.
- Acceptance criteria for this plan should not require historical v1 docs to be free of old commands.

### 9. Full-text search checklist

Run these searches before finishing:

```sh
grep -R "skillhost user" -n README.md src tests web/frontend docs/plan-v2.md
```

Expected result:

- No matches in `README.md`, `src`, `tests`, `web/frontend`, or `docs/plan-v2.md` except within the explicit historical/old-command examples in this plan that document what is being removed.
- Matches in `docs/plan-v1.md` and possibly `docs/plan-web-v1.md` are acceptable only because they are historical v1 documents.

Run a narrower enforcement search:

```sh
grep -R "skillhost user" -n README.md src tests web/frontend
```

Expected result: no matches.

Also search for individual old forms if needed:

```sh
grep -R "user add\|user update\|user link\|user unlink\|user remove\|user list\|user doctor" -n README.md src tests web/frontend
```

Expected result: no user-facing old command examples.

## Acceptance criteria

### CLI behavior

- `skillhost add --help` exits `0`.
- `skillhost update --help` exits `0`.
- `skillhost link --help` exits `0`.
- `skillhost unlink --help` exits `0`.
- `skillhost remove --help` exits `0`.
- `skillhost list --help` exits `0`.
- `skillhost doctor --help` exits `0`.
- `skillhost project add --help` exits `0`.
- `skillhost project link --help` exits `0`.
- `skillhost user add --help` fails with argparse invalid-command behavior, expected exit code `2`.
- `skillhost add <git-repo>` still clones into the configured user repos directory.
- `skillhost update [NAME]` still updates user repos.
- `skillhost link` still links user-level skills into enabled user agent targets.
- `skillhost unlink` still unlinks user-level manifest-managed links.
- `skillhost remove <name>` still removes user-level source repos safely.
- `skillhost list` still lists user-level repos and skills.
- `skillhost doctor` still checks user-level state.
- Project commands keep their existing behavior and command shape.

### Documentation and frontend copy

- README user-level examples use `skillhost add`, `skillhost update`, `skillhost link`, `skillhost unlink`, `skillhost remove`, `skillhost list`, and `skillhost doctor`.
- README does not instruct users to run `skillhost user ...`.
- Frontend hero command example uses:

```sh
skillhost add ...
skillhost link
```

- Frontend workflow examples use top-level user commands.
- Frontend project examples still use `skillhost project ...`.
- Frontend tests assert the new examples.
- `grep -R "skillhost user" -n README.md src tests web/frontend` returns no matches.

### Tests and quality gates

Run from repository root:

```sh
uv run --with pytest --with ruff ruff check .
uv run --with pytest --with ruff pytest -q
```

If frontend dependencies are installed or CI runs frontend checks, also run:

```sh
cd web/frontend
npm install
npm run build
```

or, if `node_modules` is already present:

```sh
cd web/frontend
npm run build
```

Expected results:

- Ruff passes.
- Python tests pass.
- Frontend build/typecheck passes if executed.

## Implementation order

1. Modify `src/skillhost/cli.py` parser to promote user commands to root.
2. Update Python source command suggestions from `skillhost user ...` to `skillhost ...`.
3. Add `tests/test_cli.py` for command shape and old namespace rejection.
4. Update `README.md` examples and prose.
5. Update `web/frontend/src/**/*.tsx` command copy.
6. Update `tests/web/test_skillhost_frontend.py` expected strings and add a negative assertion against `skillhost user `.
7. Run grep checks for old command strings.
8. Run Ruff and pytest.
9. Optionally run frontend build/typecheck.
10. Commit changes with a message such as:

```sh
git commit -m "Promote user commands to top level"
```

## Risks and mitigations

### Risk: breaking users who already use `skillhost user ...`

This is intentional for v2. Mitigation: README and website must clearly show the new top-level user commands.

### Risk: project commands accidentally move or conflict with user commands

Mitigation: parser tests must cover `skillhost project ...` help and at least one project command behavior or parser path.

### Risk: hidden old command strings remain in website copy

Mitigation: run the grep checks and add `assertNotIn("skillhost user ", combined)` to frontend acceptance tests.

### Risk: historical docs cause grep noise

Mitigation: distinguish enforcement paths (`README.md src tests web/frontend`) from historical plan docs (`docs/plan-v1.md`, `docs/plan-web-v1.md`).

## Completion audit checklist

Before considering v2 complete, verify each item with concrete evidence:

- [ ] `src/skillhost/cli.py` root parser contains `add`, `update`, `link`, `unlink`, `remove`, `list`, `doctor`.
- [ ] `src/skillhost/cli.py` root parser does not contain `user`.
- [ ] `skillhost user add --help` fails with invalid command.
- [ ] `skillhost add --help` works.
- [ ] `skillhost project add --help` works.
- [ ] `README.md` contains new top-level user commands.
- [ ] `README.md` contains no `skillhost user` examples.
- [ ] `web/frontend/src` contains new top-level user commands.
- [ ] `web/frontend/src` contains no `skillhost user` examples.
- [ ] `tests/web/test_skillhost_frontend.py` expects new command strings.
- [ ] CLI tests cover old namespace rejection.
- [ ] `grep -R "skillhost user" -n README.md src tests web/frontend` returns no matches.
- [ ] `uv run --with pytest --with ruff ruff check .` passes.
- [ ] `uv run --with pytest --with ruff pytest -q` passes.
- [ ] Frontend build/typecheck passes, or the reason for not running it is documented.
