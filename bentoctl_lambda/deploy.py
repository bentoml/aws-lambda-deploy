import os
from pathlib import Path

from .aws_lambda import (
    call_sam_command,
    generate_aws_lambda_cloudformation_template_file,
    generate_lambda_deployable,
    generate_lambda_resource_names,
)
from .utils import (
    console,
    create_ecr_repository_if_not_exists,
)

import bentoml


def deploy(bento_path, deployment_name, deployment_spec):
    # for now change cwd back after callign bentoml.load()
    cwd = Path.cwd()
    breakpoint()
    bento_svc = bentoml.load(bento_path)
    os.chdir(cwd)
    bento_tag = bento_svc.tag
    deployable_path = os.path.join(
        os.path.curdir,
        f"{bento_tag.name}-{bento_tag.version}-lambda-deployable",
    )

    generate_lambda_deployable(bento_path, deployable_path, deployment_spec)
    (
        _,
        stack_name,
        repo_name,
    ) = generate_lambda_resource_names(deployment_name)
    console.print(f"Created AWS Lambda deployable [b][{deployable_path}][/b]")

    template_file_path = generate_aws_lambda_cloudformation_template_file(
        deployment_name=deployment_name,
        project_dir=deployable_path,
        api_names=list(bento_svc._apis),
        bento_service_name=bento_svc.name,
        docker_context=deployable_path,
        docker_file="Dockerfile-lambda",
        docker_tag=repo_name,
        memory_size=deployment_spec["memory_size"],
        timeout=deployment_spec["timeout"],
    )
    console.print(f"Built SAM template [b][{template_file_path}][/b]")

    with console.status("Building image"):
        call_sam_command(
            [
                "build",
                "--template-file",
                template_file_path.split("/")[-1],
                "--build-dir",
                "build",
            ],
            project_dir=deployable_path,
            region=deployment_spec["region"],
        )

    with console.status("Pushing image to ECR"):
        repository_id, registry_url = create_ecr_repository_if_not_exists(
            deployment_spec["region"], repo_name
        )
        call_sam_command(
            [
                "package",
                "--template-file",
                os.path.join("build", "template.yaml"),
                "--output-template-file",
                "package-template.yaml",
                "--image-repository",
                registry_url,
            ],
            project_dir=deployable_path,
            region=deployment_spec["region"],
        )
    console.print(f"Image built and pushed [b][{registry_url}][/b]")

    with console.status("Deploying to Lambda"):
        call_sam_command(
            [
                "deploy",
                "-t",
                "package-template.yaml",
                "--stack-name",
                stack_name,
                "--image-repository",
                registry_url,
                "--capabilities",
                "CAPABILITY_IAM",
                "--region",
                deployment_spec["region"],
                "--no-confirm-changeset",
            ],
            project_dir=deployable_path,
            region=deployment_spec["region"],
        )

    return deployable_path
