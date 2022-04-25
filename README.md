# Bentoctl AWS Lambda deployment

Bentoctl is a CLI tool for deploying your machine-learning models to any cloud platforms and serving predictions via REST APIs.
It built on top of [BentoML: the unified model serving framework](https://github.com/bentoml/bentoml), and makes it easy to bring any BentoML packaged model to production.

This repo contains the Bentoctl AWS Lambda deployment operator. This operator defines the terraform configuration for deploying the Lambda function and how to build docker image that's compatible with AWS Lambda.


> **Note:** This operator is compatible with BentoML version 1.0.0 and above. For older versions, please switch to the branch `pre-v1.0` and follow the instructions in the README.md.


## Table of Contents

   * [Prerequisites](#prerequisites)
   * [Quickstart with bentoctl](#quickstart-with-bentoctl)
   * [Configuration options](#configuration-options)

<!-- Added by: jjmachan, at: Wednesday 05 January 2022 11:50:28 AM IST -->

<!--te-->

## Prerequisites

1. Bentoml - BentoML version 1.0 and greater. Please follow the [Installation guide](https://docs.bentoml.org/en/latest/quickstart.html#installation).
2. Terraform - [Terraform](https://www.terraform.io/) is a tool for building, configuring, and managing infrastructure.
3. AWS CLI installed and configured with an AWS account with permission to the Cloudformation, Lamba, API Gateway and ECR. Please follow the [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
4. Docker - Install instruction: https://docs.docker.com/installll instruction: https://www.terraform.io/downloads.html
5. A built Bento project. For this guide, we will use the Iris classifier bento from the [BentoML quickstart guide](https://docs.bentoml.org/en/latest/quickstart.html#quickstart).

## Quickstart with bentoctl

Bentoctl is a CLI tool that you can use to deploy bentos to Lambda. It helps in configuring and managing your deployments super easy.

1. Install bentoctl via pip
    ```
    $ pip install --pre bentoctl
    ```

2. Install AWS Lambda operator

    Bentoctl will install the official AWS Lambda operator and its dependencies.

    ```
    $ bentoctl operator install aws-lambda
    ```

3. Initialize deployment with bentoctl

    Follow the interactive guide to initialize deployment project.

    ```bash
    $ bentoctl init

    Bentoctl Interactive Deployment Config Builder

    Welcome! You are now in interactive mode.

    This mode will help you setup the deployment_config.yaml file required for
    deployment. Fill out the appropriate values for the fields.

    (deployment config will be saved to: ./deployment_config.yaml)

    api_version: v1
    name: demo
    operator: aws-lambda
    template: terraform
    spec:
        region: us-west-1
        timeout: 10
        memory_size: 512
    filename for deployment_config [deployment_config.yaml]:
    deployment config file exists! Should I override? [Y/n]:
    deployment config generated to: deployment_config.yaml
    ✨ generated template files.
      - bentoctl.tfvars
      - main.tf
    ```

4. Build and push AWS Lambda comptable docker image to registry

    Bentoctl will build and push the Lambda compatible docker image to the AWS ECR repository.

    ```bash
    bentoctl build -b iris_classifier:latest -f deployment_config.yaml

    Step 1/20 : FROM bentoml/bento-server:1.0.0a7-python3.7-debian-runtime
    ---> dde7b88477b1
    Step 2/20 : ARG UID=1034
    ---> Running in b8f4ae1d8b08
    ---> e6c313c8d9ea
    Step 3/20 : ARG GID=1034
    ....
    Step 20/20 : ENTRYPOINT [ "/opt/conda/bin/python", "-m", "awslambdaric" ]
    ---> Running in 4e56057f3b18
    ---> dca82bca9034
    Successfully built dca82bca9034
    Successfully tagged aws-lambda-iris_classifier:btzv5wfv665trhcu
    🔨 Image build!
    The push refers to repository [192023623294.dkr.ecr.us-west-1.amazonaws.com/quickstart]
    btzv5wfv665trhcu: digest: sha256:ffcd120f7629122cf5cd95664e4fd28e9a50e799be7bb23f0b5b03f14ca5c672 size: 3253
    32096534b881: Pushed
    f709d8f0f57d: Pushed
    7d30486f5c78: Pushed
    ...
    c1065d45b872: Pushed
    🚀 Image pushed!
    ✨ generated template files.
      - bentoctl.tfvars
    The push refers to repository [192023623294.dkr.ecr.us-west-1.amazonaws.com/quickstart]
    ```

5. Apply Deployment with Terraform

   1. Initialize terraform project
      ```bash
      terraform init
      ```

   2. Apply terraform project to create Lambda deployment

      ```bash
      terraform apply -var-file=bentoctl.tfvars -auto-approve

      aws_iam_role.lambda_exec: Creating...
      aws_apigatewayv2_api.lambda: Creating...
      aws_apigatewayv2_api.lambda: Creation complete after 1s [id=ka8h2p2yfh]
      aws_cloudwatch_log_group.api_gw: Creating...
      aws_cloudwatch_log_group.api_gw: Creation complete after 0s [id=/aws/api_gw/quickstart-gw]
      aws_apigatewayv2_stage.lambda: Creating...
      aws_iam_role.lambda_exec: Creation complete after 3s [id=quickstart-iam]
      aws_iam_role_policy_attachment.lambda_policy: Creating...
      aws_lambda_function.fn: Creating...
      aws_apigatewayv2_stage.lambda: Creation complete after 2s [id=$default]
      aws_iam_role_policy_attachment.lambda_policy: Creation complete after 1s [id=quickstart-iam-20220414203448384500000001]
      aws_lambda_function.fn: Still creating... [10s elapsed]
      aws_lambda_function.fn: Still creating... [20s elapsed]
      aws_lambda_function.fn: Still creating... [30s elapsed]
      aws_lambda_function.fn: Still creating... [40s elapsed]
      aws_lambda_function.fn: Creation complete after 41s [id=quickstart-function]
      aws_lambda_permission.api_gw: Creating...
      aws_cloudwatch_log_group.lg: Creating...
      aws_apigatewayv2_integration.lambda: Creating...
      aws_lambda_permission.api_gw: Creation complete after 0s [id=AllowExecutionFromAPIGateway]
      aws_cloudwatch_log_group.lg: Creation complete after 0s [id=/aws/lambda/quickstart-function]
      aws_apigatewayv2_integration.lambda: Creation complete after 1s [id=8gumjws]
      aws_apigatewayv2_route.root: Creating...
      aws_apigatewayv2_route.services: Creating...
      aws_apigatewayv2_route.root: Creation complete after 0s [id=jjp5f23]
      aws_apigatewayv2_route.services: Creation complete after 0s [id=8n57a1d]

      Apply complete! Resources: 11 added, 0 changed, 0 destroyed.

      Outputs:

      base_url = "https://ka8h2p2yfh.execute-api.us-west-1.amazonaws.com/"
      function_name = "quickstart-function"
      image_tag = "192023623294.dkr.ecr.us-west-1.amazonaws.com/quickstart:btzv5wfv665trhcu"
      ```

6. Test deployed endpoint

    The `iris_classifier` uses the `/classify` endpoint for receiving requests so the full URL for the classifier will be in the form `{EndpointUrl}/classify`

    ```bash
    URL=$(terraform output -json | jq -r .base_url.value)classify
    curl -i \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[5.1, 3.5, 1.4, 0.2]' \
      $URL

    HTTP/2 200
    date: Thu, 14 Apr 2022 23:02:45 GMT
    content-type: application/json
    content-length: 1
    apigw-requestid: Ql8zbicdSK4EM5g=

    0%
    ```

7. Delete deployment
    Use the `bentoctl destroy` command to remove the registry and the deployment

    ```bash
    bentoctl destroy -f deployment_config.yaml
    ```
## Configuration options

* `region`: AWS region for Lambda deployment
* `timeout`: Timeout per request
* `memory_size`: The memory for your function, set a value between 128 MB and 10,240 MB in 1-MB increments
