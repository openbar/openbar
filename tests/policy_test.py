import logging

import pytest
import sh

from . import check_container_build
from . import check_container_pull
from . import container_rm
from . import get_container_tag

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ("initial_container", "project_kwargs", "container_build"),
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
def test_build(create_project, initial_container, project_kwargs, container_build):
    project = create_project(defconfig="hello_defconfig")
    container_tag = get_container_tag(project.container_dir, "default")

    if initial_container:
        project.make(cli={"B": "1"})
    else:
        container_rm(project.container_engine, container_tag)

    if container_build is None:
        with pytest.raises(sh.ErrorReturnCode_2):
            project.make(**project_kwargs)

    else:
        stdout = project.make(**project_kwargs)

        if container_build:
            check_container_build(project, stdout[0], "default")
            stdout_length = 2
        else:
            stdout_length = 1

        assert len(stdout) == stdout_length
        assert stdout[-1] == "Hello"


def test_build_missing(project_dirs, tmp_path, create_project):
    container_file_orig = project_dirs.container_dir / "default" / "Dockerfile"
    container_dir = tmp_path / "container"
    container_file = container_dir / "default" / "Dockerfile"
    container_file.parent.mkdir(parents=True, exist_ok=True)

    project = create_project(defconfig="hello_defconfig", container_dir=container_dir)

    def container_orig():
        container_file.write_text(container_file_orig.read_text())

    def container_update():
        with open(container_file, "a") as f:
            f.write("# test comment")

    container_orig()
    container_rm(project.container_engine, get_container_tag(container_dir, "default"))
    container_update()
    container_rm(project.container_engine, get_container_tag(container_dir, "default"))
    container_orig()

    def check_make(container_build):
        stdout = project.make()

        if container_build:
            check_container_build(project, stdout[0], "default")
            stdout_length = 2
        else:
            stdout_length = 1

        assert len(stdout) == stdout_length
        assert stdout[-1] == "Hello"

    check_make(True)
    check_make(False)
    container_update()
    check_make(True)


@pytest.mark.parametrize(
    ("initial_container", "project_kwargs", "container_pull"),
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
def test_pull(create_project, initial_container, project_kwargs, container_pull):
    project = create_project(defconfig="pull_defconfig")
    container_tag = "ghcr.io/openbar/openbar-alpine:latest"

    if initial_container:
        project.make(cli={"P": "1"})
    else:
        container_rm(project.container_engine, container_tag)

    if container_pull is None:
        with pytest.raises(sh.ErrorReturnCode_2):
            project.make(**project_kwargs)

    else:
        stdout = project.make(**project_kwargs)

        if container_pull:
            check_container_pull(project, stdout[0], container_tag)
            stdout_length = 2
        else:
            stdout_length = 1

        assert len(stdout) == stdout_length
        assert stdout[-1] == "Hello"
