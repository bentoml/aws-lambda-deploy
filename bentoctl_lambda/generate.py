import os
import shutil

from bentoctl_lambda.utils import get_metadata
from bentoctl_lambda.parameters import DeploymentParams


def generate(name, spec, template_type, destination_dir):
    """
    generates the template corresponding to the template_type.

    Parameters
    ----------
    name : str
        deployment name to be used by the template. This name will be used
        to create the resource names.
    spec : dict
        The properties of the deployment (specifications) passed from the
        deployment_config's `spec` section.
    template_type: str
        The type of template that is to be generated by the operator. The
        available ones are [terraform, cloudformation]

    Returns
    -------
    generated_path : str
        The path for the generated template.
    """
    if template_type == "terraform":
        template_file_name = "terraform_default.tf"
        generated_template_file_name = "main.tf"
        generated_params_file_name = "terraform.tfvars"
    elif template_type == "cloudformation":
        template_file_name = "cloudformation_default.yaml"
        generated_template_file_name = "cloudformation.yaml"
        generated_params_file_name = "params.json"

    generated_template_file_path = os.path.join(
        destination_dir, generated_template_file_name
    )
    if not os.path.exists(generated_template_file_path):
        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), f"templates/{template_file_name}"),
            generated_template_file_path,
        )

    # generate params file 
    params = DeploymentParams(name, spec, template_type)
    params.to_params_file(os.path.join(destination_dir, generated_params_file_name))

    return generated_template_file_path
