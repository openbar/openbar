import logging

import pytest

from . import iter_containers

logger = logging.getLogger(__name__)


def pytest_generate_tests(metafunc):
    if metafunc.cls is TestSimple:
        metafunc.parametrize(
            "container", iter_containers(metafunc.config.rootpath, startswith="simple")
        )
    elif metafunc.cls is TestInitenv:
        metafunc.parametrize(
            "container", iter_containers(metafunc.config.rootpath, startswith="initenv")
        )
    elif metafunc.cls is TestYocto:
        metafunc.parametrize(
            "container", iter_containers(metafunc.config.rootpath, startswith="yocto")
        )


class TestSimple:
    @pytest.fixture
    def project_default_kwargs(self, container):
        return {"env": {"OB_CONTAINER": container}}

    def test_hello(self, create_project):
        project = create_project(defconfig="type_simple_defconfig")
        stdout = project.make()
        assert stdout[-1] == "Hello world"


class TestInitenv:
    @pytest.fixture
    def project_default_kwargs(self, container):
        return {
            "env": {"OB_CONTAINER": container},
            "type": "initenv",
            "initenv_script": "type_initenv",
        }

    def test_hello(self, create_project):
        project = create_project(defconfig="type_initenv_defconfig")
        stdout = project.make()
        assert stdout[-1] == "Hello world"


class TestYocto:
    @pytest.fixture
    def project_default_kwargs(self, container, poky_dir, project_dirs):
        return {
            "env": {
                "OB_CONTAINER": container,
                "OB_CONTAINER_VOLUMES": poky_dir,
                "DL_DIR": project_dirs.session_dir / "downloads",
                "SSTATE_DIR": project_dirs.session_dir / "sstate-cache",
            },
            "type": "yocto",
            "poky_dir": poky_dir,
            "_tty_out": False,
        }

    def test_make_native(self, create_project):
        project = create_project(defconfig="type_yocto_defconfig")
        stdout = project.make()

        have_warnings = False
        for line in stdout:
            if line.startswith("WARNING:"):
                have_warnings = True
                logger.warning(line)

        if have_warnings:
            assert stdout[-3].endswith("all succeeded.")
        else:
            assert stdout[-1].endswith("all succeeded.")
