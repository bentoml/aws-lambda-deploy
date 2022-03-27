import os
import base64

import fs
import boto3
from bentoml.bentos import Bento


def get_metadata(path: str):
    metadata = {}

    bento = Bento.from_fs(fs.open_fs(path))
    metadata["tag"] = bento.tag
    metadata["bentoml_version"] = ".".join(bento.info.bentoml_version.split(".")[:3])

    python_version_txt_path = "env/python/version.txt"
    python_version_txt_path = os.path.join(path, python_version_txt_path)
    with open(python_version_txt_path, "r") as f:
        python_version = f.read()
    metadata["python_version"] = ".".join(python_version.split(".")[:2])

    return metadata


def get_ecr_login_info(region, repository_id):
    ecr_client = boto3.client("ecr", region)
    token = ecr_client.get_authorization_token(registryIds=[repository_id])
    username, password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode("utf-8")
        .split(":")
    )
    registry_url = token["authorizationData"][0]["proxyEndpoint"]

    return registry_url, username, password


def create_ecr_repository_if_not_exists(region, repository_name):
    ecr_client = boto3.client("ecr", region)
    try:
        result = ecr_client.describe_repositories(repositoryNames=[repository_name])
        repository_id = result["repositories"][0]["registryId"]
        repository_uri = result["repositories"][0]["repositoryUri"]
    except ecr_client.exceptions.RepositoryNotFoundException:
        result = ecr_client.create_repository(repositoryName=repository_name)
        repository_id = result["repository"]["registryId"]
        repository_uri = result["repository"]["repositoryUri"]
    return repository_id, repository_uri
