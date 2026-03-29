<p align="center">
  <img src="docs/images/openbar.png" alt="OpenBar" width="150">
</p>

<h1 align="center">OpenBar</h1>

<p align="center">
  <a href="https://openbar.readthedocs.io"><img src="https://readthedocs.org/projects/openbar/badge/" alt="Documentation"></a>
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/openbar/openbar/actions/workflows/pytest.yml"><img src="https://github.com/openbar/openbar/actions/workflows/pytest.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/pre-commit/pre-commit"><img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit"></a>
  <a href="https://github.com/openbar/openbar/commits/main"><img src="https://img.shields.io/github/last-commit/openbar/openbar" alt="Last commit"></a>
</p>

<br>

Complex projects are hard to build reproducibly. Every developer has a slightly
different host setup, CI runs on a different OS, and the "reference build machine"
is a mystery box that someone set up three years ago and nobody dares to touch.

OpenBar solves this by running your entire build inside a container, while keeping
the user interface as simple as possible:

```bash
make myconfig_defconfig  # select a configuration
make                     # build
```

No Docker commands, no setup scripts, no environment variables to remember.

## How it works

OpenBar wraps your build targets in a container defined by a `Dockerfile` in your
project. The container is built or pulled automatically when needed. Your source
files and build outputs stay on the host filesystem, owned by you — not root.

Build targets are defined in a plain `.config` file using standard Makefile syntax:
no new language to learn, and the full GNU Make feature set is available.

## Features

- **Containerised builds** — Podman or Docker, your choice. No dependency on the
  host distribution.
- **Minimal interface** — `make <config>` then `make`. Works the same for every
  developer, on every machine, and in CI.
- **Makefile config files** — Define targets, variables, and dependencies in
  familiar syntax. Conditions, includes, functions — all supported.
- **Multiple configurations** — Ship as many `defconfig` files as you need.
  Switch between them instantly, or build them all at once with `make foreach`.
- **Any project type** — Works with [Yocto][yocto], [Buildroot][buildroot],
  [Zephyr][zephyr], or any custom build system.
- **Transparent SSH forwarding** — Your SSH keys and agent are forwarded into
  the container automatically.
- **Debug access** — Drop into the build environment at any time with
  `make shell`.

[yocto]: https://www.yoctoproject.org
[buildroot]: https://buildroot.org
[zephyr]: https://www.zephyrproject.org

## Getting started

The quickest way to create a new project is with the setup wizard:

```bash
curl -sSf https://openbar.github.io/openbar/wizard.sh | sh
```

See the [documentation][docs] for the full installation guide, configuration
reference, and examples.

[docs]: https://openbar.readthedocs.io

## License

OpenBar is released under the [MIT License](LICENSE.md).
