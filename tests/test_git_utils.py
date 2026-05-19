from skillhost.git_utils import normalize_git_url


def test_normalize_git_url_common_forms():
    assert normalize_git_url("git@github.com:org/repo.git") == "github.com/org/repo"
    assert normalize_git_url("git@github.com:org/repo") == "github.com/org/repo"
    assert normalize_git_url("https://github.com/org/repo.git") == "github.com/org/repo"
    assert normalize_git_url("https://github.com/org/repo") == "github.com/org/repo"
    assert normalize_git_url("ssh://git@github.com/org/repo.git") == "github.com/org/repo"
    assert normalize_git_url("https://gitlab.com/group/repo.git") == "gitlab.com/group/repo"
