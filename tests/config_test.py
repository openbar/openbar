import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ("defconfig", "make_kwargs", "expected"),
    [
        # 3.1.1 Splitting Long Lines
        ("splitting_defconfig", {}, ["foo bar baz", "foo bar baz"]),
        # 6.2.1 Recursively Expanded Variable Assignment
        ("recursive_expansion_defconfig", {}, ["after", "after"]),
        # 6.2.2 Simply Expanded Variable Assignment
        ("simple_expansion_defconfig", {}, ["before", "after"]),
        ("simple_expansion_2_defconfig", {}, ["before", "after"]),
        # 6.2.4 Conditional Variable Assignment
        ("conditional_defconfig", {"cli": {"TEST_VAR": "env"}}, ["env", "default"]),
        # 6.3.1 Substitution References"
        ("substitution_defconfig", {}, ["foo.ok bar.ok", "foo.ok bar.ok"]),
        # 6.3.2 Computed Variable Names
        ("computed_defconfig", {}, ["hello", "hello"]),
        # 6.5 Setting Variables
        ("shell_defconfig", {}, ["bar", "bar"]),
        # 6.6 Appending More Text to Variables
        ("appending_defconfig", {}, ["foo bar baz", "bar baz"]),
        # 6.7 The override Directive
        (
            "override_defconfig",
            {"cli": {"TEST_VAR": "env", "TEST_VAR2": "env"}},
            ["cfg", "env cfg"],
        ),
        (
            "override_multiline_defconfig",
            {"cli": {"TEST_VAR": "env", "TEST_VAR2": "env"}},
            ["cfg", "env cfg"],
        ),
        # 6.8 Defining Multi-Line Variables
        ("multiline_defconfig", {}, ["foo", "bar", "baz", "foo bar baz"]),
        # 6.9 Undefining Variables
        ("undefining_defconfig", {}, ["one", "three", ""]),
        # 9.5 Overriding Variables
        ("overriding_defconfig", {"cli": {"TEST_VAR": "env"}}, ["env", "cfg"]),
        # 10.3 Variables Used by Implicit Rules
        ("builtin_defconfig", {}, ["ar cc g++ rm -f", "-rv"]),
    ],
)
def test_variable(project_dirs, create_project, defconfig, make_kwargs, expected):
    defconfig_dir = project_dirs.tests_data_dir / "config" / "variable"
    project = create_project(defconfig_dir=defconfig_dir, defconfig=defconfig)
    stdout = project.make(**make_kwargs)
    assert expected == stdout[-len(expected) :]


@pytest.mark.parametrize(
    ("env_var", "project_attr"),
    [
        ("OB_BUILD_DIR", "build_dir"),
        ("OB_CONTAINER_DIR", "container_dir"),
        ("OB_DEFCONFIG_DIR", "defconfig_dir"),
        ("OB_PROJECT_ID", "id"),
        ("OB_ROOT_DIR", "root_dir"),
        ("OB_TYPE", "type"),
        ("OB_VERBOSE", "verbose"),
    ],
)
def test_environment_variable(
    tmp_path, project_dirs, create_project, env_var, project_attr
):
    defconfig_dir = project_dirs.tests_data_dir / "config" / "variable"
    project = create_project(
        root_dir=tmp_path,
        build_dir=tmp_path / "build",
        defconfig_dir=defconfig_dir,
        defconfig="environment_defconfig",
        verbose=0,
    )
    stdout = project.make(cli={"ENV_VAR": env_var})
    assert stdout[-1] == str(project.get(project_attr))
