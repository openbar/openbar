import logging

import pytest

from . import CommandError
from . import command_run

logger = logging.getLogger(__name__)


@pytest.mark.no_container_engine
def test_gnu_make():
    stdout = command_run("make", "--version")
    logger.info(stdout[0])
    assert stdout[0].lower().startswith("gnu make")


@pytest.mark.no_container_engine
def test_gnu_awk():
    stdout = command_run("awk", "--version")
    logger.info(stdout[0])
    assert stdout[0].lower().startswith("gnu awk")


@pytest.mark.docker
def test_docker():
    stdout = command_run("docker", "--version")
    logger.info(stdout[0])
    assert stdout[0].lower().startswith("docker")


@pytest.mark.podman
def test_podman():
    stdout = command_run("podman", "--version")
    logger.info(stdout[0])
    assert stdout[0].lower().startswith("podman")


@pytest.mark.no_container_engine
def test_project_fixture(create_project):
    # Project creation
    project = create_project(
        defconfig="hello_defconfig",
        cli={"FOO": "create/cli", "BAR": "create/cli"},
        env={"FOO": "create/env", "BAZ": "create/env"},
    )
    assert (project.root_dir / "Makefile").exists()
    assert (project.root_dir / ".config").exists()

    # Simple command
    stdout = project.run("env")
    for var in ["FOO=create/cli", "BAR=create/cli", "BAZ=create/env"]:
        assert var in stdout

    # Command arguments
    stdout = project.run("env", "-C", project.root_dir, "pwd")
    assert stdout[0].strip() == str(project.root_dir)

    # Override command line / environment variables
    stdout = project.run(
        "env",
        cli={"FOO": "run/cli", "BAR": "run/cli"},
        env={"FOO": "run/env", "BAZ": "run/env"},
    )
    for var in ["FOO=run/cli", "BAR=run/cli", "BAZ=run/env"]:
        assert var in stdout

    # Failing command (pytest)
    with pytest.raises(CommandError):
        project.run("false")

    # Failing command (command)
    project.run("false", _ok_code=(0, 1))

    # Make command
    project.make("help")
