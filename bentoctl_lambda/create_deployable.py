import os
import shutil

path_to_aws_lambda_files = os.path.join(os.path.dirname(__file__), "./aws_lambda/")
DOCKERFILE_TEMPLATE = os.path.join(path_to_aws_lambda_files, "Dockerfile.template")
APP_FILE = os.path.join(path_to_aws_lambda_files, "app.py")


def generate_lambda_deployable(bento_path, bento_metadata, deployable_path):
    # copy bento_bundle to project_path
    shutil.copytree(bento_path, deployable_path)

    # Make docker file with dockerfile template
    dockerfile = os.path.join(deployable_path, "Dockerfile")
    with open(DOCKERFILE_TEMPLATE, "r", encoding="utf-8") as f, open(
        dockerfile, "w"
    ) as dockerfile:
        dockerfile_template = f.read()
        dockerfile.write(
            dockerfile_template.format(
                bentoml_version=bento_metadata["bentoml_version"],
                python_version=bento_metadata["python_version"],
            )
        )

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
        bento_metadata=bento_metadata,
        deployable_path=deployable_path,
    )

    additional_build_args = None

    return dockerfile_path, docker_context_path, additional_build_args
