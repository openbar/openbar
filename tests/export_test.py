import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ("defconfig", "project_kwargs", "expected"),
    [
        # Undefined variable is not exported
        ("base_defconfig", {}, None),
        # CLI variable is exported
        ("base_defconfig", {"cli": {"TEST_VAR": "cli"}}, "cli"),
        # ENV variable without OB_EXPORT is not exported
        ("base_defconfig", {"env": {"TEST_VAR": "env"}}, None),
        # ENV variable with OB_EXPORT(ENV) is exported
        (
            "base_defconfig",
            {"env": {"TEST_VAR": "env+env", "OB_EXPORT": "TEST_VAR"}},
            "env+env",
        ),
        # ENV variable with OB_EXPORT(CLI) is exported
        (
            "base_defconfig",
            {"env": {"TEST_VAR": "env+cli"}, "cli": {"OB_EXPORT": "TEST_VAR"}},
            "env+cli",
        ),
        # ENV variable with OB_EXPORT(CFG) is exported
        ("env_defconfig", {"env": {"TEST_VAR": "env+cfg"}}, "env+cfg"),
        # CFG variable is exported
        ("cfg_defconfig", {}, "cfg"),
        # Variable with space is exported properly
        (
            "base_defconfig",
            {"cli": {"TEST_VAR": "value with spaces"}},
            "value with spaces",
        ),
        # Undefined variable that have default value have their default value
        ("default_defconfig", {}, "default"),
        # Variable that have default value have their own value
        ("default_defconfig", {"cli": {"TEST_VAR": "user"}}, "user"),
        # Undefined variables that are reset have their reset value
        ("reset_defconfig", {}, "reset"),
        # Variables that are reset also have their reset value
        ("reset_defconfig", {"cli": {"TEST_VAR": "user"}}, "reset"),
        # Undefined variables that are appended have the appended value
        ("append_defconfig", {}, "append"),
        # Variables that are appended have their own value plus the appended value
        ("append_defconfig", {"cli": {"TEST_VAR": "user"}}, "user append"),
        # Undefined variables that are set in initenv are exported
        (
            "base_defconfig",
            {"type": "initenv", "initenv_script": "base_initenv"},
            "initenv",
        ),
        # Variables that are set in initenv have their initenv value
        (
            "base_defconfig",
            {
                "type": "initenv",
                "initenv_script": "base_initenv",
                "cli": {"TEST_VAR": "cli"},
            },
            "initenv",
        ),
        # Undefined variables that are appended in initenv are exported
        (
            "base_defconfig",
            {"type": "initenv", "initenv_script": "append_initenv"},
            "initenv",
        ),
        # Variables that are appended in initenv have their initenv value
        (
            "base_defconfig",
            {
                "type": "initenv",
                "initenv_script": "append_initenv",
                "cli": {"TEST_VAR": "cli"},
            },
            "cli+initenv",
        ),
        # Undefined variables that have a not exported variable in initenv are
        # not exported
        (
            "base_defconfig",
            {"type": "initenv", "initenv_script": "noexport_initenv"},
            None,
        ),
        # Variables that have a not exported variable in initenv are exported
        (
            "base_defconfig",
            {
                "type": "initenv",
                "initenv_script": "noexport_initenv",
                "cli": {"TEST_VAR": "cli"},
            },
            "no export",
        ),
    ],
)
def test_export(create_project, project_dirs, defconfig, project_kwargs, expected):
    project = create_project(
        defconfig_dir=project_dirs.tests_data_dir / "export",
        defconfig=defconfig,
        **project_kwargs,
    )
    stdout = project.make()
    assert stdout[-1] == stdout[-2]
    if expected is None:
        assert stdout[-3] == "undefined"
        assert stdout[-1] == ""
    else:
        assert stdout[-3] == "defined"
        assert stdout[-1] == expected
