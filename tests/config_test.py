import logging

import pytest

from tests import CommandError

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ("defconfig", "make_kwargs", "expected"),
    [
        # 3.1.1 Splitting Long Lines
        ("splitting_defconfig", {}, ["foo bar baz", "foo bar baz"]),
        # 3.3 Including Other Makefiles
        ("include_defconfig", {}, ["from_main_file", "from_included_file"]),
        ("sinclude_defconfig", {}, ["after_missing_include"]),
        ("dashinclude_defconfig", {}, ["after_missing_include"]),
        # 6.2.1 Recursively Expanded Variable Assignment
        ("recursive_expansion_defconfig", {}, ["after", "after"]),
        # 6.2.2 Simply Expanded Variable Assignment
        ("simple_expansion_defconfig", {}, ["before", "after"]),
        # 6.2.3 Immediately Expanded Variable Assignment
        ("simple_expansion_2_defconfig", {}, ["before", "after"]),
        # 6.2.4 Conditional Variable Assignment
        ("conditional_defconfig", {"cli": {"TEST_VAR": "env"}}, ["env", "default"]),
        # 6.3.1 Substitution References
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


@pytest.mark.parametrize(
    ("defconfig", "make_kwargs", "expected"),
    [
        # 7.2 Syntax of Conditionals
        ("ifeq_defconfig", {}, ["ifeq_true", "ifeq_false"]),
        ("ifneq_defconfig", {}, ["ifneq_true", "ifneq_false"]),
        ("ifdef_defconfig", {}, ["ifdef_true", "ifdef_false"]),
        ("ifndef_defconfig", {}, ["ifndef_true", "ifndef_false"]),
    ],
)
def test_conditional(project_dirs, create_project, defconfig, make_kwargs, expected):
    defconfig_dir = project_dirs.tests_data_dir / "config" / "conditional"
    project = create_project(defconfig_dir=defconfig_dir, defconfig=defconfig)
    stdout = project.make(**make_kwargs)
    assert expected == stdout[-len(expected) :]


@pytest.mark.parametrize(
    ("defconfig", "make_kwargs", "expected"),
    [
        # 8.2 Functions for String Substitution and Analysis
        (
            "string_defconfig",
            {},
            [
                "foo BAR baz",
                "foo Bar Baz",
                "foo bar",
                "bar",
                "bar baz",
                "foo baz",
                "bar baz foo",
                "bar",
                "foo bar",
                "3",
                "foo",
                "baz",
            ],
        ),
        # 8.3 Functions for File Names
        (
            "filename_defconfig",
            {},
            [
                "/some/path/to/",
                "file.c",
                ".c",
                "/some/path/to/file",
                "foo.bak bar.bak",
                "/dir/foo /dir/bar",
                "foo.c bar.h",
                "",
                "/bar",
                "",
            ],
        ),
        # 8.4 Functions for Conditionals
        ("if_defconfig", {}, ["yes", "no", "fallback", "result", ""]),
        # 8.6 The foreach Function
        ("foreach_defconfig", {}, ["item_a item_b item_c"]),
        # 8.8 The call Function
        ("call_defconfig", {}, ["world hello"]),
        # 8.9 The value Function
        ("value_defconfig", {}, ["", "hello"]),
        # 8.10 The eval Function
        ("eval_defconfig", {}, ["hello"]),
        # 8.11 The origin Function
        ("origin_defconfig", {}, ["file", "undefined", "environment"]),
        # 8.12 The flavor Function
        ("flavor_defconfig", {}, ["recursive", "simple", "undefined"]),
        # 8.13 Functions That Control Make — $(info ...) / $(warning ...)
        # $(warning ...) goes to stderr and is not checked here.
        ("info_defconfig", {}, ["info_message", "done"]),
        # 8.14 The shell Function
        ("shell_defconfig", {}, ["hello", "foo"]),
    ],
)
def test_function(project_dirs, create_project, defconfig, make_kwargs, expected):
    defconfig_dir = project_dirs.tests_data_dir / "config" / "function"
    project = create_project(defconfig_dir=defconfig_dir, defconfig=defconfig)
    stdout = project.make(**make_kwargs)
    assert expected == stdout[-len(expected) :]


@pytest.mark.parametrize(
    ("defconfig", "make_kwargs", "expected"),
    [
        # 4.3 Types of Prerequisites
        ("prereq_defconfig", {}, ["setup", "build"]),
        # 4.3 Order-only Prerequisites
        ("order_only_defconfig", {}, ["init", "main"]),
        # 4.13 Multiple Targets in a Rule
        ("multiple_defconfig", {}, ["multiple", "multiple"]),
        # 5.2 Recipe Echoing — @command suppresses Make's command echo
        ("at_defconfig", {}, ["at_result"]),
        # 5.5 Errors in Recipes
        ("error_defconfig", {}, ["continues"]),
        # OpenBar QUIET variable — redirects output to /dev/null when OB_VERBOSE=0
        ("quiet_defconfig", {}, ["always"]),
        # OpenBar OB_MANUAL_TARGETS — lowercase target forced manual, not run by default
        ("manual_targets_defconfig", {}, ["auto"]),
    ],
)
def test_target(project_dirs, create_project, defconfig, make_kwargs, expected):
    defconfig_dir = project_dirs.tests_data_dir / "config" / "target"
    project = create_project(defconfig_dir=defconfig_dir, defconfig=defconfig)
    stdout = project.make(**make_kwargs)
    assert expected == stdout[-len(expected) :]


@pytest.mark.no_container_engine
def test_function_error(project_dirs, create_project):
    # 8.13 Functions That Control Make — $(error ...) stops config parsing.
    defconfig_dir = project_dirs.tests_data_dir / "config" / "function"
    project = create_project(defconfig_dir=defconfig_dir, defconfig="error_defconfig")
    with pytest.raises(CommandError):
        project.make()
