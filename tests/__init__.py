import os
import re
from pathlib import Path


def container_tag(directory, container="default"):
    def sanitize(string):
        string = re.sub(r"(^[^a-z\d]|[^a-z\d]$)", "", str(string).lower())
        string = re.sub(r"[^a-z\d-]", ".", string.replace("_", "-"))
        return string[:128]

    project = sanitize(directory.name)
    image = f"{project}/{sanitize(container)}"
    tag = f"{image}:{sanitize(os.environ['USER'])}"

    return tag


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
