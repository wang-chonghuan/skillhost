"""Small wrappers around git commands."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from .errors import GitError, SkillhostError


def run_git(args: list[str], cwd: str | Path | None = None) -> subprocess.CompletedProcess[str]:
    cmd = ["git", *args]
    try:
        return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
    except FileNotFoundError as exc:
        raise GitError("git is not available on PATH") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        detail = stderr or stdout or str(exc)
        raise GitError(f"git command failed: {' '.join(cmd)}\n{detail}") from exc


def clone_url(url: str) -> str:
    """Return the URL used for cloning, preferring SSH for GitHub HTTPS URLs."""
    raw = url.strip()
    parsed = urlparse(raw)
    if parsed.scheme in {"http", "https"} and (parsed.hostname or "").lower() == "github.com":
        path = parsed.path.strip("/")
        if path.endswith(".git"):
            path = path[:-4]
        if path and "/" in path:
            return f"git@github.com:{path}.git"
    return raw


def clone_repo(url: str, dest: str | Path, branch: str | None = None) -> None:
    args = ["clone"]
    if branch:
        args.extend(["--branch", branch])
    args.extend([clone_url(url), str(dest)])
    run_git(args)


def pull_ff_only(repo: str | Path) -> None:
    if is_dirty(repo):
        raise SkillhostError(f"Refusing to update dirty repository: {repo}")
    run_git(["pull", "--ff-only"], cwd=repo)


def is_git_repo(path: str | Path) -> bool:
    try:
        run_git(["rev-parse", "--is-inside-work-tree"], cwd=path)
        return True
    except GitError:
        return False


def is_dirty(repo: str | Path) -> bool:
    result = run_git(["status", "--porcelain"], cwd=repo)
    return bool(result.stdout.strip())


def get_origin_url(repo: str | Path) -> str:
    return run_git(["remote", "get-url", "origin"], cwd=repo).stdout.strip()


def get_repo_root(path: str | Path = ".") -> Path:
    return Path(run_git(["rev-parse", "--show-toplevel"], cwd=path).stdout.strip()).resolve()


def normalize_git_url(url: str) -> str:
    """Normalize common SSH/HTTPS Git URLs to host/org/repo."""
    raw = url.strip()
    if not raw:
        raise SkillhostError("Git URL cannot be empty")

    # SCP-like: git@github.com:org/repo.git or user@host:path/repo
    scp = re.match(r"^(?:[^@/]+@)?([^:/]+):/?(.+)$", raw)
    if scp and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
        host, path = scp.groups()
    else:
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
        host = parsed.hostname or parsed.netloc
        path = parsed.path.lstrip("/")
    host = (host or "").lower()
    path = path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    path = re.sub(r"/+", "/", path)
    if not host or not path or "/" not in path:
        raise SkillhostError(f"Could not normalize Git URL: {url}")
    return f"{host}/{path}"


def derive_repo_name(git_url: str) -> str:
    normalized = normalize_git_url(git_url)
    return normalized.rsplit("/", 1)[-1]
