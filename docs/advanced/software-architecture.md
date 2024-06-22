# Software Architecture

<!-- TODO: Replace with actual Make layer chain.
  The content below is outdated (references old Yocto-specific files that no longer exist).
  The real chain is:
    main.mk
    └─ container.mk  (podman.mk or docker.mk)
       └─ [container run]
          └─ type.mk  (simple.mk / initenv.mk / yocto.mk)
             └─ config.mk
                └─ user .config file

  Key points to document:
  - Each layer is a separate Make invocation (-f flag)
  - Variables cross the container boundary only via the environment (OB_EXPORT)
  - config-load-variables is called multiple times; OVERRIDE=1 only on first call (main.mk)
  - All config targets are declared .PHONY unconditionally via OB_ALL_TARGETS in common.mk
  - Target classification: lowercase = auto, uppercase/symbol = manual; OB_MANUAL_TARGETS overrides
-->

```
- make
  \_ make -f <root_dir>/openbar/core/container.mk
    \_ podman/docker run ...
      \_ make -f <root_dir>/openbar/core/type.mk
        \_ make -f <root_dir>/openbar/core/config.mk
          \_ user .config targets
```
