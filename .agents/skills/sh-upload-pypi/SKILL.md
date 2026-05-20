---
name: sh-upload-pypi
description: Safely publish a Python package to PyPI from a git repository. Use when the user wants to release, upload, or publish to PyPI with a token stored in a txt file, and the workflow should sync with remote, commit all changes, push, build distributions, and upload with standard safe steps.
---

# sh-upload-pypi

Use this skill to publish a Python package to PyPI only after the user provides a PyPI token txt file path. If no token file path was provided, ask for it and stop.

## Non-negotiable safety rules

- Never print, echo, paste, log, or summarize the token value.
- Read the token from the provided txt file only; do not ask the user to paste the token into chat.
- Disable shell tracing before reading the token (`set +x`).
- Do not write `.pypirc` unless the user explicitly asks.
- Do not force-push.
- Do not tag releases unless the user explicitly asks or the repo release docs require it.
- Stop on failed tests, build, artifact check, push, or upload.
- Stop if the target version already exists on PyPI.

## Required order

The safe default order is:

1. preflight
2. commit all local changes if any
3. pull/rebase from remote
4. push
5. clean build artifacts
6. build and check distributions
7. upload to PyPI
8. report result

Commit before rebase when the tree is dirty; rebasing with uncommitted changes is fragile. If the tree is clean, fetch/rebase can happen immediately after preflight.

## Workflow

### 1. Preflight

- Confirm repo root: `git rev-parse --show-toplevel`.
- Confirm token file exists and is readable: `[ -r "$TOKEN_FILE" ]`.
- Confirm current branch and upstream: `git branch --show-current` and `git rev-parse --abbrev-ref --symbolic-full-name @{u}`.
- Identify package name and version from `pyproject.toml` or project metadata.
- Inspect `git status --short`.
- Run cheap standard validation if the repo has an obvious command, such as `uv run pytest`, `pytest`, or the repo's documented test command.
- Check whether the target version already exists on PyPI; if it exists, stop and ask for a version bump.

### 2. Commit all local changes

Stage and commit only if there are staged changes:

```bash
git add -A
git diff --cached --stat
if ! git diff --cached --quiet; then
  git commit -m "Release <package> <version>"
fi
```

Do not use `git commit ... || true`; it can hide real commit failures.

### 3. Pull/rebase and push

```bash
git fetch origin
git pull --rebase
git push
```

If rebase conflicts occur, stop and report the conflicted files. Do not continue to build or publish.

### 4. Clean, build, and check artifacts

```bash
rm -rf dist/ build/ ./*.egg-info ./src/*.egg-info
uv run --with build python -m build
uv run --with twine python -m twine check dist/*
```

If `uv` is unavailable, use the project's existing environment and run equivalent `python -m build` and `python -m twine check dist/*` commands.

### 5. Upload without exposing the token

Prefer Twine environment variables over `-p` so the token is not placed directly in the command arguments:

```bash
set +x
TOKEN=$(tr -d '[:space:]' < "$TOKEN_FILE")
TWINE_USERNAME=__token__ TWINE_PASSWORD="$TOKEN" \
  uv run --with twine python -m twine upload dist/*
unset TOKEN TWINE_PASSWORD TWINE_USERNAME
```

If `uv` is unavailable, use:

```bash
set +x
TOKEN=$(tr -d '[:space:]' < "$TOKEN_FILE")
TWINE_USERNAME=__token__ TWINE_PASSWORD="$TOKEN" \
  python -m twine upload dist/*
unset TOKEN TWINE_PASSWORD TWINE_USERNAME
```

If upload says the file or version already exists, stop and tell the user to bump the version; PyPI does not allow replacing an existing distribution file.

## Stop and ask the user when

- no token txt file path was provided
- the token file cannot be read
- package name or version cannot be determined
- package version appears inconsistent across files
- target version already exists on PyPI
- branch has no upstream and a safe push target is unclear
- rebase has conflicts
- validation, build, artifact check, push, or upload fails

## Response style while running

Keep updates short:

- preflight complete
- committed changes or nothing to commit
- rebased successfully
- pushed successfully
- built and checked artifacts
- uploaded successfully

Final response should include package name, version, PyPI project URL, and final git status summary. Never include the token value.
