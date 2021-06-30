import sys
import os

from bentoml.saved_bundle import load_bento_service_metadata

from utils import (
    get_configuration_value,
    create_s3_bucket_if_not_exists,
    create_ecr_repository_if_not_exists,
    build_docker_image,
    push_docker_image_to_repository,
    get_ecr_login_info,
    generate_docker_image_tag,
)
from awslambda import (
    generate_lambda_deployment,
    generate_lambda_resource_names,
    generate_aws_lambda_cloudformation_template_file,
    call_sam_command,
)


def deploy_aws_lambda(bento_bundle_path, deployment_name, config_json):
    bento_metadata = load_bento_service_metadata(bento_bundle_path)
    lambda_config = get_configuration_value(config_json)
    deployable_path = os.path.join(
        os.path.curdir,
        f"{bento_metadata.name}-{bento_metadata.version}-lambda-deployable",
    )

    print("Creating AWS Lambda deployable")
    generate_lambda_deployment(bento_bundle_path, deployable_path, lambda_config)
    (
        template_name,
        stack_name,
        s3_bucket_name,
        repo_name,
    ) = generate_lambda_resource_names(deployment_name)

    print("Creating S3 bucket for cloudformation")
    s3_bucket_name = "yataitest1"
    create_s3_bucket_if_not_exists(s3_bucket_name, lambda_config["region"])

    print("Build and push image to ECR")
    repository_id, registry_url = create_ecr_repository_if_not_exists(
        lambda_config["region"], repo_name
    )
    _, username, password = get_ecr_login_info(lambda_config["region"], repository_id)
    ecr_tag = generate_docker_image_tag(
        registry_url, bento_metadata.name, bento_metadata.version
    )
    build_docker_image(
        context_path=deployable_path,
        dockerfile="Dockerfile-lambda",
        image_tag=ecr_tag,
    )
    push_docker_image_to_repository(
        repository=ecr_tag, username=username, password=password
    )

    print("Building SAM template")
    api_names = [api.name for api in bento_metadata.apis]
    template_file_path = generate_aws_lambda_cloudformation_template_file(
        project_dir=deployable_path,
        api_names=api_names,
        bento_service_name=bento_metadata.name,
        ecr_image_uri=ecr_tag,
        memory_size=lambda_config["memory_size"],
        timeout=lambda_config["timeout"],
    )
    print("SAM Template file generated at ", template_file_path)
    return_code, stdout, stderr = call_sam_command(
        [
            "deploy",
            "-t",
            template_file_path.split("/")[-1],
            "--stack-name",
            "iris-classifier",
            "--image-repository",
            ecr_tag,
            "--capabilities",
            "CAPABILITY_IAM",
            "--region",
            lambda_config["region"],
            "--no-confirm-changeset",
        ],
        project_dir=deployable_path,
        region=lambda_config["region"],
    )
    if return_code != 0:
        print(return_code, stdout, stderr)
    else:
        print("Upload success!")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception(
            "Please provide bundle path, deployment and path to lambda"
            " config file (optional)"
        )
    bento_bundle_path = sys.argv[1]
    deployment_name = sys.argv[2]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "lambda_config.json"

    deploy_aws_lambda(bento_bundle_path, deployment_name, config_json)
