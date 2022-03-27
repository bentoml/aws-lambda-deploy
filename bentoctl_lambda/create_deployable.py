from logging import shutdown
import os
import shutil

from bentoctl_lambda.utils import get_metadata


def generate_lambda_deployable(bento_path, deployable_path):
    bento_metadata = get_metadata(bento_path)
    # set base path
    path_to_templates = os.path.join(os.path.dirname(__file__), "./aws_lambda/")

    # copy bento_bundle to project_path
    shutil.copytree(bento_path, deployable_path)

    # Make docker file with dockerfile template
    template_file = os.path.join(path_to_templates, "Dockerfile.template")
    dockerfile = os.path.join(deployable_path, "Dockerfile")
    with open(template_file, "r", encoding="utf-8") as f:
        dockerfile_template = f.read()
    with open(dockerfile, "w") as dockerfile:
        dockerfile.write(
            dockerfile_template.format(
                bentoml_version=bento_metadata["bentoml_version"],
                python_version=bento_metadata["python_version"],
            )
        )

    # copy the entrypoint
    shutil.copy(
        os.path.join(path_to_templates, "entry.sh"),
        os.path.join(deployable_path, "entry.sh"),
    )

    # copy the config file for bento
    shutil.copy(
        os.path.join(path_to_templates, "config.yml"),
        os.path.join(deployable_path, "config.yml"),
    )

    # Copy app.py which handles the Lambda events
    shutil.copy(
        os.path.join(path_to_templates, "app.py"),
        os.path.join(deployable_path, "app.py"),
    )


def create_deployable(bento_path, destination_dir, overwrite_deployable):
    """
    The deployable is the bento along with all the modifications (if any)
    requried to deploy to the cloud service.

    Returns
    -------
    dockerfile_path : str
        path to the dockerfile.
    docker_context_path : str
        path to the docker context.
    additional_build_args : dict
        Any addition build arguments that need to be passed to the
        docker build command
    """

    # TODO: Make deployable dir name related to bento service name and version
    deployable_path = os.path.join(destination_dir, "bentoctl_deployable")
    docker_context_path = deployable_path
    dockerfile_path = os.path.join(deployable_path, "Dockerfile")

    if os.path.exists(deployable_path):
        if overwrite_deployable:
            print(f"Overwriting existing deployable [{deployable_path}]")
            shutil.rmtree(deployable_path)
        else:
            print("Using existing deployable")
            return dockerfile_path, docker_context_path, additional_build_args

    generate_lambda_deployable(
        bento_path=bento_path,
        deployable_path=deployable_path,
    )

    additional_build_args = None

    return dockerfile_path, docker_context_path, additional_build_args
