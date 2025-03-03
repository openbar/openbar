import logging
import re

import pytest
import sh

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.parametrize(
    "container",
    [
        "simple/almalinux-9",
        "simple/alpine",
        "simple/archlinux",
        "simple/debian-12",
        "simple/fedora-41",
        "simple/opensuse-15.6",
        "simple/rockylinux-9",
        "simple/ubuntu-24.04",
        "yocto/almalinux-9",
        "yocto/debian-12",
        "yocto/fedora-40",
        "yocto/rockylinux-9",
        "yocto/ubuntu-24.04",
    ],
)


@pytest.fixture
def project_default_kwargs(container):
    return {
        "env": {"OB_CONTAINER": container},
        "cli": {"V": 1},
        "_err_to_out": True,
    }


def test_hello(create_project):
    project = create_project(defconfig="container_defconfig")
    stdout = project.make()
    assert stdout[-1] == "Hello"


def test_uid_gid(create_project):
    project = create_project(defconfig="container_defconfig")

    def get_uid_gid(stdout):
        matches = re.match(r"uid=(?P<uid>\d+).* gid=(?P<gid>\d+)", stdout)
        return (matches["uid"], matches["gid"])

    local_uid, local_gid = get_uid_gid(sh.id())

    stdout = project.make("id")
    container_uid, container_gid = get_uid_gid(stdout[-1])

    assert local_uid == container_uid
    assert local_gid == container_gid


def test_home(create_project):
    project = create_project(defconfig="container_defconfig")
    stdout = project.make("home")
    assert stdout[-1] == "/home/container"


def test_volumes(create_project, project_dirs):
    test_file = project_dirs.session_dir / "test_dir/test_file"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.touch(exist_ok=True)

    project = create_project(defconfig="container_defconfig")
    stdout = project.make(
        "volumes",
        env={"OB_CONTAINER_VOLUMES": f"{test_file} {test_file}:/opt/test_file:ro"},
        cli={"TEST_FILE": str(test_file)},
    )

    assert stdout[-1] == str(project.root_dir)
