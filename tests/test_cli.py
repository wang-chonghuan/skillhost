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


@pytest.mark.parametrize(
    "command",
    ["register", "unregister", "add", "update", "remove", "relink", "unlink", "list", "projects", "agents", "doctor", "config"],
)
def test_top_level_command_help_works(command):
    assert_exits([command, "--help"], 0)


def test_root_command_list_has_v7_commands():
    parser = build_parser()
    subparsers = next(action for action in parser._actions if getattr(action, "dest", None) == "command")
    command_names = set(subparsers.choices)
    assert {
        "init",
        "register",
        "unregister",
        "add",
        "update",
        "remove",
        "relink",
        "unlink",
        "list",
        "projects",
        "agents",
        "doctor",
        "config",
    } <= command_names
