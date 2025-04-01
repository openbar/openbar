import logging

import pytest

from . import iter_containers

logger = logging.getLogger(__name__)


@pytest.hookimpl
def pytest_generate_tests(metafunc):
    metafunc.parametrize(
        "container", iter_containers(metafunc.config.rootpath, startswith="yocto")
    )


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
