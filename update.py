import sys

from utils import console
from deploy import deploy


def update(bento_bundle_path, deployment_name, config_json):
    """
    in the case of AWS Lambda deployments, since we are using SAM cli for deploying
    the updation and deployment process is identical, hence you can just call the
    deploy functionality for updation also.
    """
    deploy(bento_bundle_path, deployment_name, config_json)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception("Please provide deployment name, bundle path and API name")
    bento_bundle_path = sys.argv[1]
    deployment_name = sys.argv[2]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "lambda_config.json"

    update(bento_bundle_path, deployment_name, config_json)
    console.print("[bold green]Updation Complete!")
