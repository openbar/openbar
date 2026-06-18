# Configuration

The `.config` file is a standard Makefile included by OpenBar after the
container layer. It defines your project's build targets and configuration.

## Auto and manual targets

By default, lowercase targets are *automatic*: they run when you call `make`
with no arguments. Uppercase or symbol targets are *manual* by default.

```make title=".config"
build:          # automatic — lowercase
	do something

CLEAN:          # manual — uppercase
	do something else
```

Use [`OB_MANUAL_TARGETS`](../reference/variables.md#OB_MANUAL_TARGETS) to
override the convention for specific targets:

```make title=".config"
OB_MANUAL_TARGETS += deploy

deploy:         # manual — overridden via OB_MANUAL_TARGETS
	do something
```

<!-- TODO: Document OB_AUTO_TARGETS override as well -->

## Exporting environment variables

<!-- TODO: Document OB_EXPORT:
  - Variables listed in OB_EXPORT are passed from host environment into the container
  - The `override VAR = value` pattern in defconfig automatically adds VAR to OB_EXPORT
  - Why this is needed: sub-Make processes only inherit environment variables, not Make variables
  - Example: exporting MACHINE, DL_DIR, SSTATE_DIR for Yocto builds
-->

## Mounting directories

<!-- TODO: Document OB_CONTAINER_VOLUMES:
  - Space-separated list of volume mount specs
  - Formats: <host path>, <host path>:<container path>, <host path>:<container path>:<options>
  - OB_ROOT_DIR and OB_BUILD_DIR are mounted automatically
  - Common use: mount shared Yocto download/sstate cache directories
-->
