import logging
import os
import subprocess  # nosec
from typing import List

from little_cheesemonger._errors import LittleCheesemongerError
from little_cheesemonger._platform import get_python_binaries
from little_cheesemonger._types import ConfigurationType

LOGGER = logging.getLogger(__name__)


def run(configuration: ConfigurationType) -> None:
    """Run build environment setup per configuration."""

    if configuration["environment_variables"] is not None:
        set_environment_variables(configuration["environment_variables"])

    if configuration["system_dependencies"] is not None:
        install_system_dependencies(configuration["system_dependencies"])

    if configuration["python_dependencies"] is not None:
        install_python_dependencies(configuration["python_dependencies"])

    if configuration["steps"] is not None:
        execute_steps(configuration["steps"])


def set_environment_variables(variables: List[str]) -> None:
    """Set environment variables."""

    variables_expanded = {}

    for variable in variables:
        try:
            key, value = variable.split("=")
            variables_expanded[key] = value
        except ValueError:
            raise LittleCheesemongerError(
                "Unable to extract key and value from envrionment "
                f"variable {variable}. Environment variables must be "
                "set in KEY=VALUE format."
            )

    os.environ.update(variables_expanded)


def install_system_dependencies(dependencies: List[str]) -> None:
    """Install system dependencies."""

    run_subprocess(["yum", "install", "-y"] + dependencies)


def install_python_dependencies(dependencies: List[str]) -> None:
    """Install Python dependencies."""

    for binaries in get_python_binaries().values():
        run_subprocess([str(binaries / "pip"), "install"] + dependencies)


def execute_steps(commands: List[str]) -> None:
    """Execute multiple commands."""

    for command in commands:
        run_subprocess(command.split(" "))


def run_subprocess(command: List[str]) -> None:
    """Run subprocess."""

    try:
        subprocess.run(" ".join(command), check=True, shell=True)  # nosec
    except subprocess.CalledProcessError as e:
        raise LittleCheesemongerError(f"Subprocess error: {e.stderr}")
