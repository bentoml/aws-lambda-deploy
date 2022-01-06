import boto3
from botocore.exceptions import ClientError

from .aws_lambda import generate_lambda_resource_names


def describe(deployment_name, deployment_spec):
    # get data about cf stack
    _, stack_name, repo_name = generate_lambda_resource_names(deployment_name)
    cf_client = boto3.client("cloudformation", deployment_spec["region"])
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
