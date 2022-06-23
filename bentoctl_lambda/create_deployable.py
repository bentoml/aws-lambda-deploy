from __future__ import annotations

import os
import shutil
from sys import version_info
from pathlib import Path
from typing import Any

if version_info >= (3, 8):
    from shutil import copytree
else:
    from backports.shutil_copytree import copytree

from bentoml._internal.bento.bento import BentoInfo
from bentoml._internal.bento.build_config import DockerOptions
from bentoml._internal.bento.gen import generate_dockerfile
from bentoml._internal.utils import bentoml_cattr

LAMBDA_DIR = Path(os.path.dirname(__file__), "aws_lambda")
TEMPLATE_PATH = LAMBDA_DIR.joinpath("template.j2")
APP_PATH = LAMBDA_DIR.joinpath("app.py")


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

    if deployable_path.exists():
        if not overwrite_deployable:
            print("Using existing deployable")
            return str(deployable_path)

    bento_metafile = Path(bento_path, "bento.yaml")
    with bento_metafile.open("r", encoding="utf-8") as metafile:
        info = BentoInfo.from_yaml_file(metafile)

    options = bentoml_cattr.unstructure(info.docker)
    options["dockerfile_template"] = TEMPLATE_PATH

    dockerfile_path = deployable_path.joinpath("env", "docker", "Dockerfile")
    with dockerfile_path.open("w", encoding="utf-8") as dockerfile:
        dockerfile.write(
            generate_dockerfile(
                DockerOptions(**options).with_defaults(),
                str(deployable_path),
                use_conda=any(
                    i is not None
                    for i in bentoml_cattr.unstructure(info.conda).values()
                ),
            )
        )

    # copy over app.py file
    shutil.copy(str(APP_PATH), os.path.join(deployable_path, "app.py"))

    return str(deployable_path)
