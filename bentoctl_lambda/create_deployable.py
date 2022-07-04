from __future__ import annotations

import os
import shutil
from pathlib import Path
from sys import version_info
from typing import Any

from attr import asdict

if version_info >= (3, 8):
    from shutil import copytree
else:
    from backports.shutil_copytree import copytree

from bentoml._internal.bento.bento import BentoInfo
from bentoml._internal.bento.build_config import DockerOptions
from bentoml._internal.bento.gen import generate_dockerfile

LAMBDA_DIR = Path(os.path.dirname(__file__), "aws_lambda")
TEMPLATE_PATH = LAMBDA_DIR.joinpath("template.j2")
APP_PATH = LAMBDA_DIR.joinpath("app.py")
ENTRY_SCRIPT = LAMBDA_DIR.joinpath("entry_script.sh")
AWS_LAMBDA_RIE = LAMBDA_DIR.joinpath("aws-lambda-rie-x86")
BENTOML_CONFIG_FILE = LAMBDA_DIR.joinpath("bentoml_server_config.yaml")


def create_deployable(
    bento_path: str,
    destination_dir: str,
    bento_metadata: dict[str, Any],
    overwrite_deployable: bool,
) -> str:
    """
    The deployable is the bento along with all the modifications (if any)
    requried to deploy to the cloud service.

    Parameters
    ----------
    bento_path: str
        Path to the bento from the bento store.
    destination_dir: str
        directory to create the deployable into.
    bento_metadata: dict
        metadata about the bento.

    Returns
    -------
    docker_context_path : str
        path to the docker context.
    """

    deployable_path = Path(destination_dir)
    copytree(bento_path, deployable_path, dirs_exist_ok=True)

    bento_metafile = Path(bento_path, "bento.yaml")
    with bento_metafile.open("r", encoding="utf-8") as metafile:
        info = BentoInfo.from_yaml_file(metafile)

    options = asdict(info.docker)
    options["dockerfile_template"] = TEMPLATE_PATH

    dockerfile_path = deployable_path.joinpath("env", "docker", "Dockerfile")
    with dockerfile_path.open("w", encoding="utf-8") as dockerfile:
        dockerfile_generated = generate_dockerfile(
            DockerOptions(**options).with_defaults(),
            str(deployable_path),
            use_conda=not info.conda.is_empty(),
        )
        dockerfile.write(dockerfile_generated)

    # copy over app.py file
    shutil.copy(str(APP_PATH), os.path.join(deployable_path, "app.py"))

    # the entry_script.sh file that will be the entrypoint
    shutil.copy(
        str(ENTRY_SCRIPT),
        os.path.join(deployable_path, "env", "docker", "entry_script.sh"),
    )

    # aws-lambda runtime-interface-emulator - check docs for more info
    shutil.copy(
        str(AWS_LAMBDA_RIE),
        os.path.join(deployable_path, "aws-lambda-rie"),
    )

    # bentoml_config_file to dissable /metrics
    shutil.copy(
        str(BENTOML_CONFIG_FILE),
        os.path.join(deployable_path, "bentoml_config.yaml"),
    )

    return str(deployable_path)
