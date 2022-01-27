import logging
import os
import re
import shutil
import subprocess

import yaml

from bentoctl_lambda.utils import get_metadata

logger = logging.getLogger(__name__)


def generate_lambda_deployable(bento_path, project_path, lambda_config):
    bento_metadata = get_metadata(bento_path)
    current_dir_path = os.path.dirname(__file__)

    # copy bento_bundle to project_path
    shutil.copytree(bento_path, project_path)

    # Make docker file with dockerfile template
    template_file = os.path.join(current_dir_path, "Dockerfile.template")
    dockerfile = os.path.join(project_path, "Dockerfile-lambda")
    with open(template_file, "r", encoding="utf-8") as f:
        dockerfile_template = f.read()

    with open(dockerfile, "w") as dockerfile:
        dockerfile.write(
            dockerfile_template.format(
                bentoml_version=bento_metadata["bentoml_version"],
                python_version=bento_metadata["python_version"],
            )
        )
    # shutil.copy(
    #     os.path.join(current_dir_path, "Dockerfile"),
    #     os.path.join(project_path, "Dockerfile-lambda"),
    # )
    #
    # copy the entrypoint
    shutil.copy(
        os.path.join(current_dir_path, "entry.sh"),
        os.path.join(project_path, "entry.sh"),
    )

    # copy the config file for bento
    shutil.copy(
        os.path.join(current_dir_path, "config.yml"),
        os.path.join(project_path, "config.yml"),
    )

    # Copy app.py which handles the Lambda events
    shutil.copy(
        os.path.join(current_dir_path, "app.py"), os.path.join(project_path, "app.py")
    )


def generate_aws_compatible_string(*items, max_length=63):
    """
    Generate a AWS resource name that is composed from list of string items. This
    function replaces all invalid characters in the given items into '-', and allow user
    to specify the max_length for each part separately by passing the item and its max
    length in a tuple, e.g.:

    >> generate_aws_compatible_string("abc", "def")
    >> 'abc-def'  # concatenate multiple parts

    >> generate_aws_compatible_string("abc_def")
    >> 'abc-def'  # replace invalid chars to '-'

    >> generate_aws_compatible_string(("ab", 1), ("bcd", 2), max_length=4)
    >> 'a-bc'  # trim based on max_length of each part
    """
    trimmed_items = [
        item[0][: item[1]] if type(item) == tuple else item for item in items
    ]
    items = [item[0] if type(item) == tuple else item for item in items]

    for i in range(len(trimmed_items)):
        if len("-".join(items)) <= max_length:
            break
        else:
            items[i] = trimmed_items[i]

    name = "-".join(items)
    if len(name) > max_length:
        raise Exception(
            "AWS resource name {} exceeds maximum length of {}".format(name, max_length)
        )
    invalid_chars = re.compile("[^a-zA-Z0-9-]|_")
    name = re.sub(invalid_chars, "-", name)
    return name


def generate_lambda_resource_names(name):
    sam_template_name = generate_aws_compatible_string(f"{name}-template")
    deployment_stack_name = generate_aws_compatible_string(f"{name}-stack")
    # repo should be (?:[a-z0-9]+(?:[._-][a-z0-9]+)*/)*[a-z0-9]+(?:[._-][a-z0-9]+)*''
    repo_name = generate_aws_compatible_string(f"{name}-repo").lower()

    return sam_template_name, deployment_stack_name, repo_name


def generate_docker_image_tag(registry_uri, bento_name, bento_version):
    image_tag = f"{bento_name}-{bento_version}".lower()
    return f"{registry_uri}:{image_tag}"


def generate_aws_lambda_cloudformation_template_file(
    deployment_name,
    project_dir,
    api_names,
    bento_service_name,
    docker_tag,
    docker_file,
    docker_context,
    memory_size: int,
    timeout: int,
):
    template_file_path = os.path.join(project_dir, "template.yaml")
    sam_config = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Globals": {
            "Function": {"Timeout": timeout, "MemorySize": memory_size},
            "Api": {
                "BinaryMediaTypes": ["*~1*"],
                "Cors": "'*'",
                "Auth": {
                    "ApiKeyRequired": False,
                    "DefaultAuthorizer": "NONE",
                    "AddDefaultAuthorizerToCorsPreflight": False,
                },
            },
        },
        "Resources": {},
    }
    for api_name in api_names:
        sam_config["Resources"][api_name] = {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                "FunctionName": f"{deployment_name}-{api_name}",
                "PackageType": "Image",
                "ImageConfig": {"Command": [f"app.{api_name}"]},
                "Events": {
                    "Api": {
                        "Type": "Api",
                        "Properties": {
                            "Path": "/{}".format(api_name),
                            "Method": "post",
                        },
                    }
                },
                "Environment": {
                    "Variables": {
                        "BENTOML_BENTO_SERVICE_NAME": bento_service_name,
                        "BENTOML_API_NAME": api_name,
                    }
                },
            },
            "Metadata": {
                "DockerTag": docker_tag,
                "Dockerfile": docker_file,
                "DockerContext": "./",
            },
        }

    with open(template_file_path, "w") as f:
        yaml.dump(sam_config, f, default_flow_style=False)

    # We add Outputs section separately, because the value should not
    # have "'" around !Sub
    with open(template_file_path, "a") as f:
        f.write(
            """\
Outputs:
  EndpointUrl:
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.\
amazonaws.com/Prod"
    Description: URL for endpoint
"""
        )
    return template_file_path


def call_sam_command(command, project_dir, region):
    command = ["sam"] + command
    logger.debug(f"SAM Command: {' '.join(command)}")

    # We are passing region as part of the param, due to sam cli is not currently
    # using the region that passed in each command.  Set the region param as
    # AWS_DEFAULT_REGION for the subprocess call
    copied_env = os.environ.copy()
    copied_env["AWS_DEFAULT_REGION"] = region

    proc = subprocess.Popen(
        command,
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=copied_env,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        raise Exception(
            f"SAM command failed with return code {proc.returncode}.\n"
            f"stdout: {stdout.decode('utf-8')}\n"
            f"stderr: {stderr.decode('utf-8')}"
        )
    else:
        logger.debug(f"SAM Command stdout: {stdout.decode('utf-8')}")