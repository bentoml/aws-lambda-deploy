import sys
import boto3
import json
from botocore.exceptions import ClientError

from awslambda import generate_lambda_resource_names


def describe_lambda_deployment(deployment_name):
    # get data about cf stack
    _, stack_name, repo_name = generate_lambda_resource_names(deployment_name)
    cf_client = boto3.client("cloudformation")
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

    # import pdb; pdb.set_trace()
    print(json.dumps(info_json, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Please provide deployment name")
    deployment_name = sys.argv[1]

    describe_lambda_deployment(deployment_name)
