import os
from pathlib import Path


def iter_containers(rootpath, only_file=None, startswith=None):
    container_dir = rootpath / "wizard/container"
    for root, _, filenames in os.walk(container_dir, followlinks=True):
        for file in [Path(root) / f for f in filenames]:
            if file.name != "Dockerfile":
                continue

            if only_file and file != file.resolve():
                continue

            container = str(file.parent.relative_to(container_dir))

            if startswith and not container.startswith(startswith):
                continue

            yield str(file.parent.relative_to(container_dir))
