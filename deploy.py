import sys


def deploy_aws_lambda(bento_bundle_path, deployment_name, config_json):
    pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception("Please provide deployment name, bundle path and API name")
    bento_bundle_path = sys.argv[1]
    deployment_name = sys.argv[2]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "lambda_config.json"

    deploy_aws_lambda(bento_bundle_path, deployment_name, config_json)
