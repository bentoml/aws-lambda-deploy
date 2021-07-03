# aws-lambda-deploy
Deploy BentoML models to AWS Lambda

## Prerequisites

- An active AWS account configured on the machine with AWS CLI installed and configured
    - Install instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
    - Configure AWS account instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
- Docker is installed and running on the machine.
    - Install instruction: https://docs.docker.com/install

- Install required python packages
    - `$ pip install -r requirements.txt`


## Deploy IrisClassifier from BentoML quick start guide to AWS Lambda

1. Build and save Bento Bundle from [BentoML quick start guide](https://github.com/bentoml/BentoML/blob/master/guides/quick-start/bentoml-quick-start-guide.ipynb)

2. Create Lambda  deployment with the deployment tool

    Run deploy script in the command line:

    ```bash
    $ BENTO_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
    $ python deploy.py $BENTO_BUNDLE_PATH my-lambda-deployment lambda_config.json

    # Sample output
    Creating AWS Lambda deployable
    Building SAM template
    Building Image
    0
    Build Succeeded
    Built Artifacts
    ...
    CloudFormation outputs from deployed stack
    -------------------------------------------------------------------------------------------------
    Outputs
    -------------------------------------------------------------------------------------------------
    Key                 EndpointUrl
    Description         URL for endpoint
    Value               https://j2gm5zn7z9.execute-api.us-west-1.amazonaws.com/Prod
    -------------------------------------------------------------------------------------------------

    Successfully created/updated stack - my-lambda-deployment-stack in us-west-1

3. Get deployment information and status

```bash
$ python describe.py my-lambda-deployment

# Sample output
{
  "StackId": "arn:aws:cloudformation:us-west-1:192023623294:stack/my-lambda-deployment-stack/29c15040-db7a-11eb-a721-028d528946df",
  "StackName": "my-lambda-deployment-stack",
  "StackStatus": "CREATE_COMPLETE",
  "CreationTime": "07/02/2021, 21:12:09",
  "LastUpdatedTime": "07/02/2021, 21:12:20",
  "EndpointUrl": "https://j2gm5zn7z9.execute-api.us-west-1.amazonaws.com/Prod"
}
```

4. Make sample request to Lambda deployment

```bash
curl -i \
  --header "Content-Type: application/json" \
  --request POST \
  --data '[[5.1, 3.5, 1.4, 0.2]]' \
  https://j2gm5zn7z9.execute-api.us-west-1.amazonaws.com/Prod/predict
```

5. Delete Lambda deployment

```bash
$ python delete.py my-lambda-deployment

# Sample output
Delete CloudFormation Stack my-lambda-deployment-stack
Delete ECR repo my-lambda-deployment-repo
```

## Deployment operations

### Create a deployment

Use CLI

```
```bash
python deploy.py <Bento_bundle_path> <Deployment_name> <Config_JSON default is lambda_config.json>
```

Example:

```bash
MY_BUNDLE_PATH=${bentoml get IrisClassifier:latest --print-location -q)
python deploy.py $MY_BUNDLE_PATH my_first_deployment lambda_config.json
```

Use Python API

```python
from deploy import deploy_aws_lambda

deploy_aws_lambda(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

#### Available configuration options for Lambda deployments

* `region`: AWS region for EC2 deployment
* `timeout`: Timeout per request
* `memory_size`: The memory for your function, set a value between 128 MB and 10,240 MB in 1-MB increments

### Update a deployment

Use CLI

```bash
python update.py <Bento_bundle_path> <Deployment_name> <Config_JSON>
```

Use Python API

```python
from update import update_aws_lambda
update_aws_lambda(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

### Get deployment's status and information

Use CLI

```bash
python describe.py <Deployment_name> <Config_JSON>
```

Use Python API

```python
from describe import describe_deployment
describe_deployment(DEPLOYMENT_NAME, CONFIG_JSON)
```

### Delete deployment

Use CLI

```bash
python delete.py <Deployment_name> <Config_JSON>
```

Use Python API

```python
from  delete import delete_deployment
delete_deployment(DEPLOYMENT_NAME, CONFIG_JSON)
```