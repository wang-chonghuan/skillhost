"""Application errors and exit codes."""

SUCCESS = 0
USER_ERROR = 1
GIT_ERROR = 2
INTERNAL_ERROR = 3


class SkillhostError(Exception):
    """Base class for expected skillhost errors."""

    exit_code = USER_ERROR

    def __init__(self, message: str, *, exit_code: int | None = None):
        super().__init__(message)
        if exit_code is not None:
            self.exit_code = exit_code


class GitError(SkillhostError):
    """Raised when a git command fails."""

    exit_code = GIT_ERROR
