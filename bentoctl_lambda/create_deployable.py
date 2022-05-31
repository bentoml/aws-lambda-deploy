import os
import shutil

from bentoctl.docker_utils import DOCKERFILE_PATH
from bentoml._internal.bento.build_config import DockerOptions
from bentoml._internal.bento.gen import generate_dockerfile

path_to_aws_lambda_files = os.path.join(os.path.dirname(__file__), "./aws_lambda/")
BENTOML_USER_TEMPLATE = os.path.join(
    path_to_aws_lambda_files, "bentoctl_user_template.j2"
)
APP_FILE = os.path.join(path_to_aws_lambda_files, "app.py")


def generate_lambda_deployable(bento_path, bento_metadata, deployable_path):
    # copy bento_bundle to project_path
    shutil.copytree(bento_path, deployable_path)

    # Make docker file with user template
    docker_options_for_lambda = DockerOptions(dockerfile_template=BENTOML_USER_TEMPLATE)
    dockerfile_generated = generate_dockerfile(
        docker_options_for_lambda.with_defaults(), use_conda=False
    )
    dockerfile = os.path.join(deployable_path, DOCKERFILE_PATH)
    with open(dockerfile, "w") as dockerfile:
        dockerfile.write(dockerfile_generated)

    # copy over app.py file
    shutil.copy(
        APP_FILE,
        os.path.join(deployable_path, "app.py"),
    )


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

    generate_lambda_deployable(
        bento_path=bento_path,
        bento_metadata=bento_metadata,
        deployable_path=deployable_path,
    )

    return docker_context_path
