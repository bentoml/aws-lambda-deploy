import sys
import boto3
import json
from botocore.exceptions import ClientError

from aws_lambda import generate_lambda_resource_names
from utils import get_configuration_value


def describe_lambda_deployment(deployment_name, config_file_path):
    # get data about cf stack
    _, stack_name, repo_name = generate_lambda_resource_names(deployment_name)
    lambda_config = get_configuration_value(config_file_path)
    cf_client = boto3.client("cloudformation", lambda_config["region"])
    try:
        stack_info = cf_client.describe_stacks(StackName=stack_name)
    except ClientError:
        print(f"Unable to find {deployment_name} in your cloudformation stack.")
        return

    info_json = {}
    stack_info = stack_info.get("Stacks")[0]
    keys = [
        "StackName",
        "StackId",
        "StackStatus",
    ]
    info_json = {k: v for k, v in stack_info.items() if k in keys}
    info_json["CreationTime"] = stack_info.get("CreationTime").strftime(
        "%m/%d/%Y, %H:%M:%S"
    )
    info_json["LastUpdatedTime"] = stack_info.get("LastUpdatedTime").strftime(
        "%m/%d/%Y, %H:%M:%S"
    )

    # get Endpoints
    outputs = stack_info.get("Outputs")
    outputs = {o["OutputKey"]: o["OutputValue"] for o in outputs}
    info_json.update(outputs)

    return info_json


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception(
            "Please provide deployment name and the optional configuration file"
        )
    deployment_name = sys.argv[1]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "lambda_config.json"

    info_json = describe_lambda_deployment(deployment_name, config_json)
    print(json.dumps(info_json, indent=2))
