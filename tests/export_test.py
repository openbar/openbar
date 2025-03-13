import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ("defconfig", "target", "project_kwargs", "expected"),
    [
        # Undefined variable is not exported
        ("export_defconfig", "test_export", {}, None),
        # CLI variable is exported
        ("export_defconfig", "test_export", {"cli": {"TEST_VAR": "cli"}}, "cli"),
        # ENV variable without OB_EXPORT is not exported
        ("export_defconfig", "test_export", {"env": {"TEST_VAR": "env"}}, None),
        # ENV variable with OB_EXPORT(ENV) is exported
        (
            "export_defconfig",
            "test_export",
            {"env": {"TEST_VAR": "env+env", "OB_EXPORT": "TEST_VAR"}},
            "env+env",
        ),
        # ENV variable with OB_EXPORT(CLI) is exported
        (
            "export_defconfig",
            "test_export",
            {"env": {"TEST_VAR": "env+cli"}, "cli": {"OB_EXPORT": "TEST_VAR"}},
            "env+cli",
        ),
        # ENV variable with OB_EXPORT(CFG) is exported
        (
            "export_defconfig",
            "test_env_cfg",
            {"env": {"TEST_ENV_VAR": "env+cfg"}},
            "env+cfg",
        ),
        # CFG variable is exported
        ("export_defconfig", "test_cfg", {}, "cfg"),
        # Variable with space is exported properly
        (
            "export_defconfig",
            "test_export",
            {"cli": {"TEST_VAR": "value with spaces"}},
            "value with spaces",
        ),
        # Undefined variable that have default value have their default value
        ("export_defconfig", "test_default", {}, "default"),
        # Variable that have default value have their own value
        (
            "export_defconfig",
            "test_default",
            {"cli": {"TEST_DEFAULT_VAR": "user"}},
            "user",
        ),
        # Undefined variables that are reset have their reset value
        ("export_defconfig", "test_reset", {}, "reset"),
        # Variables that are reset also have their reset value
        (
            "export_defconfig",
            "test_reset",
            {"cli": {"TEST_RESET_VAR": "user"}},
            "reset",
        ),
        # Undefined variables that are appended have the appended value
        ("export_defconfig", "test_append", {}, "append"),
        # Variables that are appended have their own value plus the appended value
        (
            "export_defconfig",
            "test_append",
            {"cli": {"TEST_APPEND_VAR": "user"}},
            "user append",
        ),
        # Undefined variables that are set in initenv are exported
        (
            "export_defconfig",
            "test_initenv",
            {"type": "initenv", "initenv_script": "export_initenv"},
            "initenv",
        ),
        # Variables that are set in initenv have their initenv value
        (
            "export_defconfig",
            "test_initenv",
            {
                "type": "initenv",
                "initenv_script": "export_initenv",
                "cli": {"TEST_INITENV_VAR": "cli"},
            },
            "initenv",
        ),
        # Undefined variables that are appended in initenv are exported
        (
            "export_defconfig",
            "test_initenv_append",
            {"type": "initenv", "initenv_script": "export_initenv"},
            "initenv",
        ),
        # Variables that are appended in initenv have their initenv value
        (
            "export_defconfig",
            "test_initenv_append",
            {
                "type": "initenv",
                "initenv_script": "export_initenv",
                "cli": {"TEST_INITENV_APPEND_VAR": "cli"},
            },
            "cli+initenv",
        ),
        # Undefined variables that have a not exported variable in initenv are
        # not exported
        (
            "export_defconfig",
            "test_initenv_noexport",
            {"type": "initenv", "initenv_script": "export_initenv"},
            None,
        ),
        # Variables that have a not exported variable in initenv are exported
        (
            "export_defconfig",
            "test_initenv_noexport",
            {
                "type": "initenv",
                "initenv_script": "export_initenv",
                "cli": {"TEST_INITENV_NOEXPORT_VAR": "cli"},
            },
            "no export",
        ),
    ],
)
def test_export(create_project, defconfig, target, project_kwargs, expected):
    project = create_project(defconfig=defconfig, **project_kwargs)
    stdout = project.make(target)
    assert stdout[-1] == stdout[-2]
    if expected is None:
        assert stdout[-3] == "undefined"
        assert stdout[-1] == ""
    else:
        assert stdout[-3] == "defined"
        assert stdout[-1] == expected
