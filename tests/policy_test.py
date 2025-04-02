import logging

import pytest
import sh

from . import container_tag

logger = logging.getLogger(__name__)


@pytest.fixture
def project_default_kwargs(project_dirs, request):
    function = request.function.__name__
    root_dir = project_dirs.session_dir / f"policy_{function}"
    return {"root_dir": root_dir}


@pytest.mark.parametrize(
    ("project_kwargs", "container_delete", "build_success", "container_build"),
    [
        # Without config and without image, the container is built
        ({}, True, True, True),
        # Without config and with image, the container is not built
        ({}, False, True, False),
        # With B=0 and with image, the container is not built
        ({"cli": {"B": "0"}}, False, True, False),
        # With B=0 and without image, the container is not built
        ({"cli": {"B": "0"}}, True, False, None),
        # With B=1 and without image, the container is built
        ({"cli": {"B": "1"}}, True, True, True),
        # With B=1 and with image, the container is built
        ({"cli": {"B": "1"}}, False, True, True),
        # With FORCE_BUILD=0 and with image, the container is not built
        ({"env": {"OB_CONTAINER_FORCE_BUILD": "0"}}, False, True, False),
        # With FORCE_BUILD=0 and without image, the container is not built
        ({"env": {"OB_CONTAINER_FORCE_BUILD": "0"}}, True, False, None),
        # With FORCE_BUILD=1 and without image, the container is built
        ({"env": {"OB_CONTAINER_FORCE_BUILD": "1"}}, True, True, True),
        # With FORCE_BUILD=1 and with image, the container is built
        ({"env": {"OB_CONTAINER_FORCE_BUILD": "1"}}, False, True, True),
        # With POLICY=always and with image, the container is built
        ({"env": {"OB_CONTAINER_POLICY": "always"}}, False, True, True),
        # With POLICY=always and without image, the container is built
        ({"env": {"OB_CONTAINER_POLICY": "always"}}, True, True, True),
        # With POLICY=missing and with image, the container is not built
        ({"env": {"OB_CONTAINER_POLICY": "missing"}}, False, True, False),
        # With POLICY=missing and without image, the container is built
        ({"env": {"OB_CONTAINER_POLICY": "missing"}}, True, True, True),
        # With POLICY=never and with image, the container is not built
        ({"env": {"OB_CONTAINER_POLICY": "never"}}, False, True, False),
        # With POLICY=never and without image, the container is not built
        ({"env": {"OB_CONTAINER_POLICY": "never"}}, True, False, None),
        # With POLICY=never, FORCE_BUILD=0 but with B=1, the container is built
        (
            {
                "env": {
                    "OB_CONTAINER_POLICY": "never",
                    "OB_CONTAINER_FORCE_BUILD": "0",
                },
                "cli": {"B": "1"},
            },
            True,
            True,
            True,
        ),
        # With POLICY=always, FORCE_BUILD=1 but with B=0, the container is not built
        (
            {
                "env": {
                    "OB_CONTAINER_POLICY": "always",
                    "OB_CONTAINER_FORCE_BUILD": "1",
                },
                "cli": {"B": "0"},
            },
            False,
            True,
            False,
        ),
        # With POLICY=never but FORCE_BUILD=1, the container is built
        (
            {
                "env": {
                    "OB_CONTAINER_POLICY": "never",
                    "OB_CONTAINER_FORCE_BUILD": "1",
                }
            },
            True,
            True,
            True,
        ),
        # With POLICY=always, but FORCE_BUILD=0, the container is not built
        (
            {
                "env": {
                    "OB_CONTAINER_POLICY": "always",
                    "OB_CONTAINER_FORCE_BUILD": "0",
                }
            },
            False,
            True,
            False,
        ),
    ],
)
def test_build(
    create_project, project_kwargs, container_delete, build_success, container_build
):
    project = create_project(defconfig="hello_defconfig", **project_kwargs)
    tag = container_tag(project.container_dir)

    if container_delete:
        logger.debug(f"Deleting container image '{tag}'")
        engine = sh.Command(project.container_engine)
        engine("image", "rm", "-f", tag)

    if build_success:
        stdout = project.make()
        if container_build:
            assert stdout[0] == f"Building {project.container_engine} image '{tag}'"
        assert stdout[-1] == "Hello"

    else:
        with pytest.raises(sh.ErrorReturnCode_2):
            project.make()
