# Project Types

OpenBar supports three project types, selected during setup and stored in
[`OB_TYPE`](../reference/variables.md#OB_TYPE).

## `simple`

<!-- TODO: Describe the simple type:
  - No environment initialisation script
  - The container runs make targets directly
  - Best for: Buildroot, custom build systems, anything that doesn't need a sourced env
-->

## `initenv`

<!-- TODO: Describe the initenv type:
  - Sources an environment initialisation script before running targets
  - Script path configured via OB_INITENV_SCRIPT
  - Best for: build systems that require a sourced environment (e.g. Zephyr's west)
-->

## `yocto`

<!-- TODO: Describe the yocto type:
  - Specialisation of initenv for Yocto/OpenEmbedded projects
  - Sources oe-init-build-env (or custom script via OB_INITENV_SCRIPT)
  - Handles bitbake layer setup via OB_YOCTO_LAYERS
  - Passes variables into bitbake scope via OB_YOCTO_EXPORT_VARIABLE
  - Supports TEMPLATECONF for template-based bblayers.conf / local.conf
-->
