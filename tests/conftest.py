import logging
import os
from pathlib import Path
from shlex import quote
from textwrap import dedent
from typing import NamedTuple

import pytest
import sh
from git import Repo
from mergedeep import Strategy
from mergedeep import merge

logger = logging.getLogger(__name__)

logging.getLogger("sh").setLevel(logging.WARNING)

CONTAINER_ENGINES = ["docker", "podman"]


def command_is_available(command_name):
    try:
        sh.Command(command_name)
        return True
    except sh.CommandNotFound:
        return False


@pytest.fixture(scope="session")
def available_container_engines():
    engines = []

    for engine in CONTAINER_ENGINES:
        if command_is_available(engine):
            engines.append(engine)

    if not engines:
        raise RuntimeError("No container engine available")

    return engines


def pytest_addoption(parser):
    group = parser.getgroup("container engines")
    for engine in CONTAINER_ENGINES:
        group.addoption(
            f"--{engine}",
            action="store_true",
            help=f"run tests with the {engine} engine",
        )


def pytest_generate_tests(metafunc):
    all_markers = [m.name for m in metafunc.definition.iter_markers()]
    markers = [m for m in all_markers if m in CONTAINER_ENGINES]

    if "no_container_engine" in all_markers:
        metafunc.parametrize("container_engine", [None])
    elif not markers:
        metafunc.parametrize("container_engine", CONTAINER_ENGINES)
    else:
        metafunc.parametrize("container_engine", markers)


@pytest.fixture(autouse=True)
def _container_engine_guard(request, available_container_engines):
    all_markers = [m.name for m in request.node.iter_markers()]
    options = [e for e in CONTAINER_ENGINES if request.config.getoption(e)]

    if "no_container_engine" in all_markers:
        return

    engine = request.getfixturevalue("container_engine")

    if engine not in available_container_engines:
        pytest.skip(f"The container engine '{engine}' is not available")
    elif options and engine not in options:
        pytest.skip(f"The container engine '{engine}' is not enabled")


class ProjectDirectories(NamedTuple):
    session_dir: Path
    openbar_dir: Path
    tests_data_dir: Path
    wizard_dir: Path


@pytest.fixture(scope="session")
def project_dirs(request, tmp_path_factory):
    return ProjectDirectories(
        session_dir=tmp_path_factory.getbasetemp(),
        openbar_dir=request.config.rootpath,
        tests_data_dir=request.config.rootpath / "tests/data",
        wizard_dir=request.config.rootpath / "wizard",
    )


@pytest.fixture(scope="session")
def poky_dir(project_dirs):
    poky_url = "https://github.com/yoctoproject/poky.git"
    poky_dir = project_dirs.session_dir / "poky"
    logger.info(f"Cloning poky from {poky_url}")
    Repo.clone_from(poky_url, poky_dir)
    return poky_dir


class Project:
    def __init__(self, root_dir, project_dirs, **kwargs):
        self.__config = {
            "type": "simple",
            "root_dir": root_dir,
            "openbar_dir": project_dirs.openbar_dir,
            "defconfig_dir": project_dirs.tests_data_dir,
            "container_dir": project_dirs.wizard_dir / "container",
        }

        merge(self.__config, kwargs, strategy=Strategy.ADDITIVE)

        self.generate_makefile()

        defconfig = self.get("defconfig")
        config = self.get("config")

        if defconfig is not None:
            self.make(defconfig)
        elif config is not None:
            self.write_file(".config", config)

    def __getattr__(self, name):
        return self.__config[name]

    def get(self, name, default=None):
        return self.__config.get(name, default)

    def generate_makefile(self):
        data = f"""
            export OB_TYPE          := {self.type}
            export OB_DEFCONFIG_DIR := {self.defconfig_dir}
            export OB_CONTAINER_DIR := {self.container_dir}
        """

        if self.type == "initenv":
            data += f"""
                export OB_INITENV_SCRIPT := {self.defconfig_dir / self.initenv_script}
            """
        elif self.type == "yocto":
            data += f"""
                export OB_INITENV_SCRIPT := {self.poky_dir / "oe-init-build-env"}
            """
        elif self.type != "simple":
            raise ValueError("Invalid project type")

        data += f"""
            include {self.openbar_dir}/core/main.mk
        """

        self.write_file("Makefile", data)

    def write_file(self, file, data):
        path = self.root_dir / file
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(dedent(data))

    def run(self, command_name, *args, **kwargs):
        config = merge({}, self.__config, kwargs, strategy=Strategy.ADDITIVE)

        command_args = [
            *args,
            *[
                f"{str(k).upper()}={quote(str(v))}"
                for k, v in config.get("cli", {}).items()
            ],
        ]

        command_kwargs = {k: v for k, v in config.items() if k.startswith("_")}

        command_env = merge(
            {},
            os.environ,
            config.get("_env", {}),
            {str(k): str(v) for k, v in config.get("env", {}).items()},
        )

        command_env["LC_ALL"] = "C"

        if engine := config.get("container_engine"):
            command_env["OB_CONTAINER_ENGINE"] = engine

        command_kwargs["_env"] = command_env

        command = sh.Command(command_name)

        result = command(*command_args, **command_kwargs)

        def debug_stdout(stdout):
            for line in stdout.splitlines():
                logger.debug(line)

        if command_kwargs.get("_return_cmd", False):
            debug_stdout(result.stdout)
            return result
        debug_stdout(result)
        return result.splitlines()

    def make(self, *args, **kwargs):
        return self.run(
            "make", "--no-print-directory", "-C", self.root_dir, *args, **kwargs
        )


@pytest.fixture
def project_default_kwargs():
    return {}


@pytest.fixture
def create_project(request, tmp_path, project_default_kwargs, project_dirs):
    engine = request.getfixturevalue("container_engine")

    def _create_project(**kwargs):
        return Project(
            root_dir=tmp_path,
            project_dirs=project_dirs,
            container_engine=engine,
            **project_default_kwargs,
            **kwargs,
        )

    return _create_project
