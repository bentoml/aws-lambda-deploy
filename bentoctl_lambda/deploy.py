import os
from pathlib import Path

import bentoml

from .aws_lambda import (
    call_sam_command,
    generate_aws_lambda_cloudformation_template_file,
    generate_lambda_deployable,
    generate_lambda_resource_names,
    generate_docker_image_tag,
    run_shell_command,
)
from .utils import (
    build_docker_image_with_logs,
    console,
    create_ecr_repository_if_not_exists,
    build_docker_image,
    get_ecr_login_info,
    push_docker_image_to_repository,
)


def deploy(bento_path, deployment_name, deployment_spec):
    # init spinner
    spinner = console.status("Creating lambda deployable")
    spinner.start()

    # for now change cwd back after callign bentoml.load()
    cwd = Path.cwd()
    bento_svc = bentoml.load(bento_path)
    os.chdir(cwd)
    bento_tag = bento_svc.tag

    # generate deployable
    deployable_path = os.path.join(
        os.path.curdir,
        f"{bento_tag.name}-{bento_tag.version}-lambda-deployable",
    )
    generate_lambda_deployable(bento_path, deployable_path)
    (
        _,
        stack_name,
        repo_name,
    ) = generate_lambda_resource_names(deployment_name)
    console.print(f"Created AWS Lambda deployable [b][{deployable_path}][/b]")

    # build docker image
    spinner.update("Building docker image")
    repository_id, repository_uri = create_ecr_repository_if_not_exists(
        deployment_spec["region"], repo_name
    )
    image_tag = generate_docker_image_tag(
        repository_uri, bento_tag.name, bento_tag.version
    )
    build_docker_image_with_logs(
        build_context=deployable_path,
        image_tag=image_tag,
    )

    # docker push
    spinner.update("Pushing image into ECR")
    _, username, password = get_ecr_login_info(deployment_spec["region"], repository_id)
    push_docker_image_to_repository(image_tag, username=username, password=password)
    console.print(f"Image built and pushed [b][{repository_uri}][/b]")

    template_file_path = generate_aws_lambda_cloudformation_template_file(
        deployment_name=deployment_name,
        project_dir=deployable_path,
        api_names=list(bento_svc.apis),
        bento_service_name=bento_svc.name,
        image_uri=image_tag,
        memory_size=deployment_spec["memory_size"],
        timeout=deployment_spec["timeout"],
    )
    console.print(f"Built Cloudformation template [b][{template_file_path}][/b]")

    spinner.update("Deploying to Lambda")
    run_shell_command(
        [
            "aws",
            "--region",
            deployment_spec["region"],
            "cloudformation",
            "deploy",
            "--stack-name",
            stack_name,
            "--template-file",
            template_file_path,
            "--capabilities",
            "CAPABILITY_IAM",
        ]
    )

    return deployable_path
