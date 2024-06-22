# System Requirements

One of OpenBar's objectives is to reduce project dependencies to the bare
minimum:

- [`git`][git]
- [`repo`][repo] (optional)
- [GNU `make`][gmake]
- [GNU `awk`][gawk]
- [`podman`][podman] and / or [`docker`][docker]

[git]: https://git-scm.com
[repo]: https://gerrit.googlesource.com/git-repo/
[gmake]: https://www.gnu.org/software/make/
[gawk]: https://www.gnu.org/software/awk/
[podman]: https://podman.io
[docker]: https://www.docker.com

Some of these dependencies can be installed using your distro's package manager.

```bash title="On Debian"
apt install git make gawk
```

## Install `repo`

You can configure your project to use [`repo`][repo]. In this case, you'll
need to install it.

Many distros include `repo`, so you might be able to install from there.

```bash title="On Debian"
apt install repo # (1)!
```

1.  The `contrib` component must be enabled.

You can also install it manually:

=== "User install"

    ```bash
    mkdir -p ~/.local/bin
    curl "https://storage.googleapis.com/git-repo-downloads/repo" > ~/.local/bin/repo # (1)!
    chmod a+rx ~/.local/bin/repo
    ```

    1.  Download the script first so you can inspect it before installing.

    Make sure `~/.local/bin` is in your `PATH`:

    ```bash title=".bashrc"
    export PATH="${HOME}/.local/bin:${PATH}"
    ```

=== "System-wide"

    ```bash
    curl "https://storage.googleapis.com/git-repo-downloads/repo" > /tmp/repo # (1)!
    sudo install -m 755 /tmp/repo /usr/local/bin/repo
    ```

    1.  Download the script first so you can inspect it before installing.

??? note "Bash completion (unofficial)"

    The following installs shell completion for `repo`. This is not part of
    the official documentation and the URL may change over time.

    === "User install"

        ```bash
        mkdir -p ~/.local/share/bash-completion/completions
        curl "https://gerrit.googlesource.com/git-repo/+/refs/heads/main/completion.bash?format=TEXT" \
            | base64 -d > ~/.local/share/bash-completion/completions/repo
        ```

    === "System-wide"

        ```bash
        curl "https://gerrit.googlesource.com/git-repo/+/refs/heads/main/completion.bash?format=TEXT" \
            | base64 -d > /tmp/repo.bash-completion
        sudo install -m 644 /tmp/repo.bash-completion /usr/local/share/bash-completion/completions/repo
        ```

## Install the container engine

To use OpenBar you need to have at least one container engine:
[`podman`][podman] and / or [`docker`][docker].

=== "Podman"

    [Podman installation instructions][podman-install]
    are available in the official documentation.

=== "Docker engine"

    [Docker engine installation instructions][docker-install]
    are available in the official documentation.

    Also don't forget the [post-installation steps on Linux][docker-postinstall].

[podman-install]: https://podman.io/docs/installation
[docker-install]: https://docs.docker.com/engine/install
[docker-postinstall]: https://docs.docker.com/engine/install/linux-postinstall
