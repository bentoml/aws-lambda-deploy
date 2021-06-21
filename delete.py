import sys


def delete_deployment(bento_bundle_path, deployment_name, config_json):
    pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Please provide deployment name, bundle path and API name")
    deployment_name = sys.argv[1]

    delete_deployment(deployment_name)
