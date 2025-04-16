import logging
import os
import shlex
import subprocess
from pathlib import Path

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
    command_run(container_engine, "image", "rm", "-f", container_tag)


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


class CommandNotFoundError(FileNotFoundError):
    def __init__(self, command):
        msg = (
            f"\n\nPROCESS: {shlex.join(command)}"
            f"\n\nSTDERR:  {command[0]}: command not found"
        )
        super().__init__(msg)


class CommandError(RuntimeError):
    def __init__(self, completed):
        self.command = completed.args
        self.returncode = completed.returncode
        self.stdout = completed.stdout.decode("utf-8").splitlines()
        self.stderr = completed.stderr.decode("utf-8").splitlines()
        msg = (
            f"\n\nPROCESS: {shlex.join(completed.args)}"
            f"\n\nRETURN:  {completed.returncode}"
            f"\n\nSTDOUT:\n{completed.stdout.decode('utf-8')}"
            f"\n\nSTDERR:\n{completed.stderr.decode('utf-8')}"
        )
        super().__init__(msg)


def command_run(*args, **kwargs):
    command_parts = [str(x) for x in args]

    logger.debug(f"COMMAND: {shlex.join(command_parts)}")

    try:
        completed = subprocess.run(  # noqa: S603
            command_parts,
            shell=False,
            check=False,
            capture_output=True,
            env=kwargs.get("_env"),
        )
    except FileNotFoundError:
        raise CommandNotFoundError(command_parts)

    if completed.returncode not in kwargs.get("_ok_code", [0]):
        raise CommandError(completed)

    stdout = completed.stdout.decode("utf-8").splitlines()
    stderr = completed.stderr.decode("utf-8").splitlines()

    if not kwargs.get("_quiet", False):
        if stdout:
            logger.debug("STDOUT:")
            for line in stdout:
                logger.debug(line)
        if stderr:
            logger.debug("STDERR:")
            for line in stderr:
                logger.debug(line)

    return stdout
