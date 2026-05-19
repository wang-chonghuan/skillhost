from skillhost import config
from skillhost.git_utils import run_git
from skillhost.projects import current_project_context


def test_register_project_remote_and_match_current_repo(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("SKILLHOST_HOME", str(home))
    config.register_project("my-project", "git@github.com:org/my-project.git")
    cfg = config.load_config()
    assert cfg["projects"]["my-project"]["remotes"] == ["github.com/org/my-project"]

    repo = tmp_path / "checkout"
    repo.mkdir()
    run_git(["init"], cwd=repo)
    run_git(["remote", "add", "origin", "https://github.com/org/my-project.git"], cwd=repo)
    project, root = current_project_context(cwd=repo)
    assert project == "my-project"
    assert root == repo.resolve()
