import logging

import pytest

from . import iter_containers

logger = logging.getLogger(__name__)


@pytest.hookimpl
def pytest_generate_tests(metafunc):
    if metafunc.cls is TestSimple:
        metafunc.parametrize(
            "container", iter_containers(metafunc.config.rootpath, startswith="simple")
        )
    elif metafunc.cls is TestInitenv:
        metafunc.parametrize(
            "container", iter_containers(metafunc.config.rootpath, startswith="initenv")
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
