import hashlib
import logging
import os
from pathlib import Path

import sh

logger = logging.getLogger(__name__)


def get_container_tag(container_dir, container):
    container_file = container_dir / container / "Dockerfile"
    with open(container_file, "rb", buffering=0) as f:
        container_sha1 = hashlib.file_digest(f, "sha1").hexdigest()
    return f"openbar/{container_sha1}:latest"


def container_rm(container_engine, container_tag):
    logger.debug(f"Deleting {container_engine} image '{container_tag}'")
    engine = sh.Command(container_engine)
    engine("image", "rm", "-f", container_tag)


def check_container_build(project, stdout, container):
    container_tag = get_container_tag(project.container_dir, container)
    assert stdout == f"Building {project.container_engine} image '{container_tag}'"


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
