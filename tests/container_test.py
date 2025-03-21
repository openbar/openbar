import logging
import re

import pytest
import sh

from . import iter_containers

logger = logging.getLogger(__name__)


def pytest_generate_tests(metafunc):
    metafunc.parametrize(
        "container", iter_containers(metafunc.config.rootpath, only_file=True)
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


def test_os_release(create_project, container):
    project = create_project(defconfig="container_defconfig")
    stdout = project.make("os_release")
    image = container.split("/", 1)[1]
    if image.startswith("almalinux"):
        assert stdout[-1].startswith("Alma")
    elif image.startswith("alpine"):
        assert stdout[-1].startswith("Alpine")
    elif image.startswith("archlinux"):
        assert stdout[-1].startswith("Arch")
    elif image.startswith("debian"):
        assert stdout[-1].startswith("Debian")
    elif image.startswith("fedora"):
        assert stdout[-1].startswith("Fedora")
    elif image.startswith("opensuse"):
        assert stdout[-1].startswith("openSUSE")
    elif image.startswith("rockylinux"):
        assert stdout[-1].startswith("Rocky")
    elif image.startswith("ubuntu"):
        assert stdout[-1].startswith("Ubuntu")
    else:
        raise ValueError("Unknown container image")
