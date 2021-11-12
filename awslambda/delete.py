import sys
import argparse
import os

import boto3
from botocore.exceptions import ClientError

from .aws_lambda import generate_lambda_resource_names


def delete(deployment_name, lambda_config):
    _, stack_name, repo_name = generate_lambda_resource_names(deployment_name)
    cf_client = boto3.client("cloudformation", lambda_config["region"])
    cf_client.delete_stack(StackName=stack_name)
    print(f"Deleted CloudFormation Stack: {stack_name}")

    # delete ecr repository
    ecr_client = boto3.client("ecr", lambda_config["region"])
    try:
        ecr_client.delete_repository(repositoryName=repo_name, force=True)
        print(f"Deleted ECR repo: {repo_name}")
    except ClientError as e:
        # raise error, if the repo can't be found
        if e.response and e.response["Error"]["Code"] != "RepositoryNotFoundException":
            raise e
