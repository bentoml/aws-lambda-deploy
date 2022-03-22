import os


def create_deployable():
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
    docker_context_path = ""
    dockerfile_path = os.path.join(docker_context_path, "Dockerfile")
    additional_build_args = []
    return dockerfile_path, docker_context_path, additional_build_args
