# OpenBar

Complex projects are hard to build reproducibly. OpenBar solves this by running
your entire build inside a container, keeping the interface as simple as possible:

```bash
make myconfig_defconfig  # select a configuration
make                     # build
```

No Docker commands, no setup scripts, no environment variables to remember.

## Features

* Containerised environment using [`podman`][podman] or [`docker`][docker] —
  no dependency on the host distribution.

* Simple [`make`][make] interface with `defconfig` files — works the same for
  every developer, on every machine, and in CI.

* Configuration files are plain Makefiles — no new language to learn, full
  GNU Make feature set available.

* Multiple configurations — switch between them instantly, or build them all
  with `make foreach`.

* Transparent SSH forwarding — your keys and agent are available inside the
  container automatically.

* [Low host requirements](user-guide/system-requirements.md) —
  just `git`, `make`, `awk`, and a container engine.

* [Easy install wizard](user-guide/installation.md) to get started in minutes.

[podman]: https://podman.io
[docker]: https://www.docker.com
[make]: https://www.gnu.org/software/make/

## Why this name?

This project is intended to be a [FLOSS][floss], hence the `open` part.

The `bar` part comes from the famous `foo` and `bar` placeholder names, as this
is a generic project wrapper.

The word `openbar` adds the idea that you can use it without charge, and simply
enjoy the build.

And last but not least, the `openbar` namespace was available on GitHub.

[floss]: https://en.wikipedia.org/wiki/Free_and_open-source_software

## History

After my first [Yocto][yocto] builds, a coworker showed me that with
[`cqfd`][cqfd] (one of his projects) and a `build.sh` script he could solve the
reproducibility problem.

[`cqfd`][cqfd] was a good project, but I didn't like its configuration files.
And the `build.sh` script was very error-prone.

So I decided to create my own solution. My requirements were as follows:

* The technology used must be very common and widespread to minimize dependencies.

* The format of the configuration file used to specify build targets and recipes
  must be simple and sufficiently configurable.

* Docker containerization seemed a good solution.

The first version of OpenBar was a Makefile that ran [`cqfd`][cqfd] under the
hood. Then I added the configuration file as another `Makefile`, to run any
target in the containerized environment.

The next step was to remove `cqfd` to reduce the number of dependencies.
And [`podman`][podman] support was added as the default container engine.

The last step was to make the setup as easy as possible,
which is why the [wizard](user-guide/installation.md) was developed.

Despite having been created for Yocto, OpenBar is now generic enough
to support any type of projects:
[Yocto][yocto], [Buildroot][buildroot], [Zephyr][zephyr]...

[yocto]: https://www.yoctoproject.org
[cqfd]: https://github.com/savoirfairelinux/cqfd
[buildroot]: https://buildroot.org
[zephyr]: https://www.zephyrproject.org

## License

The OpenBar build system is released under the [MIT License][license].

[license]: https://github.com/openbar/openbar/blob/main/LICENSE.md

## Credits

Icon made by [flaticon][icon-flaticon] or [freepik][icon-freepik].

[icon-flaticon]: https://www.flaticon.com/free-icon/mai-thai_920539
[icon-freepik]: https://www.freepik.com/free-icon/mai-thai_15117327.htm
