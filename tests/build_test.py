import logging

import pytest

from . import check_container_build
from . import check_container_pull

logger = logging.getLogger(__name__)


def test_build(create_project):
    project = create_project(defconfig="hello_defconfig", cli={"B": "1"})

    stdout = project.make()

    check_container_build(project, stdout[0], "default")
    assert stdout[1] == "Hello"


@pytest.mark.parametrize(
    ("project_kwargs", "container_alpine"),
    [
        # No OB_CONTAINER_DIR and no OB_CONTAINER_IMAGE
        ({"defconfig": "hello_defconfig", "container_dir": None}, False),
        # Empty OB_CONTAINER_DIR and no OB_CONTAINER_IMAGE
        ({"defconfig": "hello_defconfig", "container_dir": ""}, False),
        # No OB_CONTAINER_DIR but OB_CONTAINER_IMAGE
        ({"defconfig": "pull_defconfig", "container_dir": None}, True),
        # Empty OB_CONTAINER_DIR but OB_CONTAINER_IMAGE
        ({"defconfig": "pull_defconfig", "container_dir": ""}, True),
        # OB_CONTAINER_DIR and OB_CONTAINER_IMAGE
        ({"defconfig": "pull_defconfig"}, True),
    ],
)
def test_pull(create_project, project_kwargs, container_alpine):
    project = create_project(cli={"P": "1"}, **project_kwargs)

    stdout = project.make()

    container_suffix = "-alpine" if container_alpine else ""
    container_tag = f"ghcr.io/openbar/openbar{container_suffix}:latest"
    check_container_pull(project, stdout[0], container_tag)
    assert stdout[1] == "Hello"
