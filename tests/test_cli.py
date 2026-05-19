import pytest

from skillhost import __version__
from skillhost.cli import build_parser, main


def assert_exits(argv: list[str], code: int) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(argv)
    assert excinfo.value.code == code


def test_version_still_works(capsys):
    assert_exits(["--version"], 0)
    assert f"skillhost {__version__}" in capsys.readouterr().out


@pytest.mark.parametrize("command", ["add", "update", "link", "unlink", "remove", "list", "doctor"])
def test_top_level_user_command_help_works(command):
    assert_exits([command, "--help"], 0)


def test_old_user_namespace_is_rejected():
    assert_exits(["user", "add", "--help"], 2)


@pytest.mark.parametrize("command", ["add", "link"])
def test_project_namespace_still_works(command):
    assert_exits(["project", command, "--help"], 0)


def test_root_command_list_has_user_commands_but_not_user_namespace():
    parser = build_parser()
    subparsers = next(action for action in parser._actions if getattr(action, "dest", None) == "command")
    command_names = set(subparsers.choices)
    assert {"add", "update", "link", "unlink", "remove", "list", "doctor", "project"} <= command_names
    assert "user" not in command_names
