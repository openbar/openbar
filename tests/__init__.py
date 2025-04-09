import logging
import os
from pathlib import Path

import sh

logger = logging.getLogger(__name__)


def get_container_tag(project_id, container_id):
    return f"localhost/openbar/{project_id}/{container_id}:latest"


def clean_container_tag(container_tag):
    if container_tag.startswith("localhost/"):
        container_tag = container_tag[10:]
    return container_tag


def container_rm(container_engine, container_tag):
    cleaned_container_tag = clean_container_tag(container_tag)
    logger.debug(f"Deleting {container_engine} image '{cleaned_container_tag}'")
    engine = sh.Command(container_engine)
    engine("image", "rm", "-f", container_tag)


def check_container_build(project, stdout, container_id):
    container_tag = clean_container_tag(get_container_tag(project.id, container_id))
    assert stdout == f"Building {project.container_engine} image '{container_tag}'"


def check_container_pull(project, stdout, container_tag):
    assert stdout == f"Pulling {project.container_engine} image '{container_tag}'"


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
