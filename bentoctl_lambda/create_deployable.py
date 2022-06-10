import os
import shutil
from pathlib import Path

from bentoctl.docker_utils import DOCKERFILE_PATH
from bentoml._internal.bento.bento import BentoInfo
from bentoml._internal.bento.gen import generate_dockerfile
from bentoml._internal.utils import bentoml_cattr

LAMBDA_DIR = Path(os.path.dirname(__file__), "aws_lambda")
TEMPLATE_PATH = LAMBDA_DIR.joinpath("template.j2")
APP_PATH = LAMBDA_DIR.joinpath("app.py")


def create_deployable(
    bento_path, destination_dir, bento_metadata, overwrite_deployable
):
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

    deployable_path = os.path.join(destination_dir, "bentoctl_deployable")
    docker_context_path = deployable_path

    if os.path.exists(deployable_path):
        if overwrite_deployable:
            print(f"Overwriting existing deployable [{deployable_path}]")
            shutil.rmtree(deployable_path)
        else:
            print("Using existing deployable")
            return docker_context_path

    bento_metafile = Path(bento_path, "bento.yaml")
    with bento_metafile.open("r") as f:
        info = BentoInfo.from_yaml_file(f)

    info.docker.dockerfile_template = TEMPLATE_PATH

    dockerfile = os.path.join(deployable_path, DOCKERFILE_PATH)
    with open(dockerfile, "w") as dockerfile:
        dockerfile.write(
            generate_dockerfile(
                info.docker,
                deployable_path,
                use_conda=any(
                    i is not None
                    for i in bentoml_cattr.unstructure(info.conda).values()
                ),
            )
        )

    # copy over app.py file
    shutil.copy(
        APP_PATH,
        os.path.join(deployable_path, "app.py"),
    )

    return docker_context_path
