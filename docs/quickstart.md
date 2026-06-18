# Quickstart

!!! info "Prerequisites"

    You need `git`, `make`, `awk` and a container engine (`podman` or `docker`).
    See [System Requirements](user-guide/system-requirements.md) for installation details.

## Create a new project

The wizard creates a ready-to-use OpenBar project by asking a few questions
(project name, type, layout, container engine).

You can [review the script][wizard-src] before running it:

``` sh
curl -sSf https://openbar.github.io/openbar/wizard.sh | sh
```

[wizard-src]: https://github.com/openbar/openbar/blob/main/wizard.sh

!!! info

    See [Installation](user-guide/installation.md) for a breakdown of each option.

## Build the project

``` sh
cd example # (1)!
make example_defconfig # (2)!
make # (3)!
```

1.  The name of the project you chose during setup.

2.  The defconfig matching your project name.

3.  That's it! :clap: :partying_face:

    You've just started a build in a fully reproducible environment.

    Now relax and enjoy a cocktail or two. :tropical_drink:

!!! info

    See [Usage](user-guide/usage.md) for more details.

## What's next?

* [Learn how to use OpenBar](user-guide/usage.md)
* [Write and customise configuration files](user-guide/configuration.md)
* [Explore project types](user-guide/project-types.md)
