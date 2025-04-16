import logging

import pytest

from . import CommandError
from . import check_container_build
from . import check_container_pull
from . import container_rm
from . import get_container_tag

logger = logging.getLogger(__name__)


def check_make(project, check_fn, check_stdout, make_kwargs):
    if check_stdout is None:
        with pytest.raises(CommandError):
            project.make(**make_kwargs)
    else:
        stdout = project.make(**make_kwargs)

        if check_stdout:
            check_fn(stdout[0])
            stdout_length = 2
        else:
            stdout_length = 1

        assert len(stdout) == stdout_length
        assert stdout[-1] == "Hello"


def check_make_build(project, check_stdout, make_kwargs={}):
    def check_fn(stdout):
        check_container_build(project, stdout, "default")

    check_make(project, check_fn, check_stdout, make_kwargs)


def check_make_pull(project, check_stdout, container_tag, make_kwargs={}):
    def check_fn(stdout):
        check_container_pull(project, stdout, container_tag)

    check_make(project, check_fn, check_stdout, make_kwargs)


@pytest.mark.parametrize(
    ("initial_container", "make_kwargs", "check_stdout"),
    [
        # With default configuration, the container is built if an image exists
        (False, {}, True),
        (True, {}, False),
        # With B=1, the container is always built
        (False, {"cli": {"B": "1"}}, True),
        (True, {"cli": {"B": "1"}}, True),
        # With B=0, the container is never built
        (False, {"cli": {"B": "0"}}, None),
        (True, {"cli": {"B": "0"}}, False),
        # With FORCE_BUILD=1, the container is always built
        (False, {"env": {"OB_CONTAINER_FORCE_BUILD": "1"}}, True),
        (True, {"env": {"OB_CONTAINER_FORCE_BUILD": "1"}}, True),
        # With FORCE_BUILD=0, the container is never built
        (False, {"env": {"OB_CONTAINER_FORCE_BUILD": "0"}}, None),
        (True, {"env": {"OB_CONTAINER_FORCE_BUILD": "0"}}, False),
        # With POLICY=always, the container is always built
        (False, {"env": {"OB_CONTAINER_POLICY": "always"}}, True),
        (True, {"env": {"OB_CONTAINER_POLICY": "always"}}, True),
        # With POLICY=newer, the container is built if an image exists
        (False, {"env": {"OB_CONTAINER_POLICY": "newer"}}, True),
        (True, {"env": {"OB_CONTAINER_POLICY": "newer"}}, False),
        # With POLICY=missing, the container is built if an image exists
        (False, {"env": {"OB_CONTAINER_POLICY": "missing"}}, True),
        (True, {"env": {"OB_CONTAINER_POLICY": "missing"}}, False),
        # With POLICY=never, the container is never built
        (False, {"env": {"OB_CONTAINER_POLICY": "never"}}, None),
        (True, {"env": {"OB_CONTAINER_POLICY": "never"}}, False),
        # B has priority over FORCE_BUILD and POLICY
        (
            False,
            {
                "env": {
                    "OB_CONTAINER_POLICY": "never",
                    "OB_CONTAINER_FORCE_BUILD": "0",
                },
                "cli": {"B": "1"},
            },
            True,
        ),
        (
            False,
            {
                "env": {
                    "OB_CONTAINER_POLICY": "always",
                    "OB_CONTAINER_FORCE_BUILD": "1",
                },
                "cli": {"B": "0"},
            },
            None,
        ),
        (
            True,
            {
                "env": {
                    "OB_CONTAINER_POLICY": "never",
                    "OB_CONTAINER_FORCE_BUILD": "0",
                },
                "cli": {"B": "1"},
            },
            True,
        ),
        (
            True,
            {
                "env": {
                    "OB_CONTAINER_POLICY": "always",
                    "OB_CONTAINER_FORCE_BUILD": "1",
                },
                "cli": {"B": "0"},
            },
            False,
        ),
        # FORCE_BUILD has priority over POLICY
        (
            False,
            {"env": {"OB_CONTAINER_POLICY": "never", "OB_CONTAINER_FORCE_BUILD": "1"}},
            True,
        ),
        (
            False,
            {"env": {"OB_CONTAINER_POLICY": "always", "OB_CONTAINER_FORCE_BUILD": "0"}},
            None,
        ),
        (
            True,
            {"env": {"OB_CONTAINER_POLICY": "never", "OB_CONTAINER_FORCE_BUILD": "1"}},
            True,
        ),
        (
            True,
            {"env": {"OB_CONTAINER_POLICY": "always", "OB_CONTAINER_FORCE_BUILD": "0"}},
            False,
        ),
    ],
)
def test_build(create_project, initial_container, make_kwargs, check_stdout):
    project = create_project(defconfig="hello_defconfig")
    container_tag = get_container_tag(project.id, "default")

    if initial_container:
        project.make(cli={"B": "1"})
    else:
        container_rm(project.container_engine, container_tag)

    check_make_build(project, check_stdout, make_kwargs)


@pytest.mark.parametrize(
    ("project_kwargs", "check_initial", "check_rebuild", "check_after_update"),
    [
        ({}, True, False, True),
        ({"env": {"OB_CONTAINER_POLICY": "always"}}, True, True, True),
        ({"env": {"OB_CONTAINER_POLICY": "newer"}}, True, False, True),
        ({"env": {"OB_CONTAINER_POLICY": "missing"}}, True, False, False),
        ({"env": {"OB_CONTAINER_POLICY": "never"}}, None, None, None),
    ],
)
def test_rebuild(
    project_dirs,
    tmp_path,
    create_project,
    project_kwargs,
    check_initial,
    check_rebuild,
    check_after_update,
):
    container_file_orig = project_dirs.container_dir / "default" / "Dockerfile"
    container_dir = tmp_path / "container"
    container_file = container_dir / "default" / "Dockerfile"
    container_file.parent.mkdir(parents=True, exist_ok=True)

    project = create_project(
        defconfig="hello_defconfig", container_dir=container_dir, **project_kwargs
    )

    container_file.write_text(container_file_orig.read_text())
    container_rm(project.container_engine, get_container_tag(project.id, "default"))

    check_make_build(project, check_initial)
    check_make_build(project, check_rebuild)

    with open(container_file, "a") as f:
        f.write("# test comment")

    check_make_build(project, check_after_update)


@pytest.mark.parametrize(
    ("initial_container", "make_kwargs", "check_stdout"),
    [
        # With default configuration, the container is pulled if an image exists
        (False, {}, True),
        (True, {}, False),
        # With P=1, the container is always pulled
        (False, {"cli": {"P": "1"}}, True),
        (True, {"cli": {"P": "1"}}, True),
        # With P=0, the container is never pulled
        (False, {"cli": {"P": "0"}}, None),
        (True, {"cli": {"P": "0"}}, False),
        # With FORCE_PULL=1, the container is always pulled
        (False, {"env": {"OB_CONTAINER_FORCE_PULL": "1"}}, True),
        (True, {"env": {"OB_CONTAINER_FORCE_PULL": "1"}}, True),
        # With FORCE_PULL=0, the container is never pulled
        (False, {"env": {"OB_CONTAINER_FORCE_PULL": "0"}}, None),
        (True, {"env": {"OB_CONTAINER_FORCE_PULL": "0"}}, False),
        # With POLICY=always, the container is always pulled
        (False, {"env": {"OB_CONTAINER_POLICY": "always"}}, True),
        (True, {"env": {"OB_CONTAINER_POLICY": "always"}}, True),
        # With POLICY=newer, the container is pulled if an image exists
        (False, {"env": {"OB_CONTAINER_POLICY": "newer"}}, True),
        (True, {"env": {"OB_CONTAINER_POLICY": "newer"}}, False),
        # With POLICY=missing, the container is pulled if an image exists
        (False, {"env": {"OB_CONTAINER_POLICY": "missing"}}, True),
        (True, {"env": {"OB_CONTAINER_POLICY": "missing"}}, False),
        # With POLICY=never, the container is never pulled
        (False, {"env": {"OB_CONTAINER_POLICY": "never"}}, None),
        (True, {"env": {"OB_CONTAINER_POLICY": "never"}}, False),
        # P has priority over FORCE_PULL and POLICY
        (
            False,
            {
                "env": {
                    "OB_CONTAINER_POLICY": "never",
                    "OB_CONTAINER_FORCE_PULL": "0",
                },
                "cli": {"P": "1"},
            },
            True,
        ),
        (
            False,
            {
                "env": {
                    "OB_CONTAINER_POLICY": "always",
                    "OB_CONTAINER_FORCE_PULL": "1",
                },
                "cli": {"P": "0"},
            },
            None,
        ),
        (
            True,
            {
                "env": {
                    "OB_CONTAINER_POLICY": "never",
                    "OB_CONTAINER_FORCE_PULL": "0",
                },
                "cli": {"P": "1"},
            },
            True,
        ),
        (
            True,
            {
                "env": {
                    "OB_CONTAINER_POLICY": "always",
                    "OB_CONTAINER_FORCE_PULL": "1",
                },
                "cli": {"P": "0"},
            },
            False,
        ),
        # FORCE_PULL has priority over POLICY
        (
            False,
            {"env": {"OB_CONTAINER_POLICY": "never", "OB_CONTAINER_FORCE_PULL": "1"}},
            True,
        ),
        (
            False,
            {"env": {"OB_CONTAINER_POLICY": "always", "OB_CONTAINER_FORCE_PULL": "0"}},
            None,
        ),
        (
            True,
            {"env": {"OB_CONTAINER_POLICY": "never", "OB_CONTAINER_FORCE_PULL": "1"}},
            True,
        ),
        (
            True,
            {"env": {"OB_CONTAINER_POLICY": "always", "OB_CONTAINER_FORCE_PULL": "0"}},
            False,
        ),
    ],
)
def test_pull(create_project, initial_container, make_kwargs, check_stdout):
    project = create_project(defconfig="pull_defconfig")
    container_tag = "ghcr.io/openbar/openbar-alpine:latest"

    if initial_container:
        project.make(cli={"P": "1"})
    else:
        container_rm(project.container_engine, container_tag)

    check_make_pull(project, check_stdout, container_tag, make_kwargs)
