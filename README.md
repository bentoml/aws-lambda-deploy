<div align="center">
    <h1> AWS Lambda Operator </h1>
    <p>
        <img src="https://user-images.githubusercontent.com/5261489/148166548-7b83bb3c-4818-4017-81f9-57cd8fb7872c.png" alt="aws lambda logo" width=25%/>
    </p>
</div>

AWS Lambda is a great service for quickly deploy service to the cloud for immediate
access. It's ability to auto scale resources base on usage make it attractive to
user who want to save cost and want to scale base on usage without administrative overhead.


<!--ts-->

## Table of Contents

   * [Prerequisites](#prerequisites)
   * [Quickstart with bentoctl](#quickstart-with-bentoctl)
   * [Quickstart with scripts](#quickstart-with-scripts)
   * [Configuration options](#configuration-options)
   * [Deployment operations](#deployment-operations)
      * [Create a deployment](#create-a-deployment)
      * [Update a deployment](#update-a-deployment)
      * [Get deployment's status and information](#get-deployments-status-and-information)
      * [Delete deployment](#delete-deployment)

<!-- Added by: jjmachan, at: Wednesday 05 January 2022 11:50:28 AM IST -->

<!--te-->

## Prerequisites

- An active AWS account configured on the machine with AWS CLI installed and configured
    - Install instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
    - Configure AWS account instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
- AWS SAM CLI (>=1.27). Installation instructions https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
- Docker is installed and running on the machine.
    - Install instruction: https://docs.docker.com/install
- (Optional) bentoctl
    - `$ pip install bentoctl`

## Quickstart with bentoctl

Bentoctl is a CLI tool that you can use to deploy bentos to Lambda. It helps in configuring and managing your deployments super easy. 

1. Install bentoctl via pip
```
$ pip install bentoctl
```

2. Add AWS Lambda operator
```
$ bentoctl operator add aws-lambda
```

3. Deploy to lambda. When you call `bentoctl deploy` without passing a deployment_config.yaml it will launch interactive program to generate `deployment_config.yaml` file for your deployment.
```
$ bentoctl deploy --display-deployment-info

Bentoctl Interactive Deployment Spec Builder

Welcome! You are now in interactive mode.

This mode will help you setup the deployment_spec.yaml file required for
deployment. Fill out the appropriate values for the fields.

(deployment spec will be saved to: ./deployment_spec.yaml)

api_version: v1
metadata:
    name: test
    operator: aws-lambda
spec:
    bento: testservice
    region: us-west-1
    timeout: 10
    memory_size: 512
    
filename for deployment_spec [deployment_spec.yaml]:
deployment spec file exists! Should I override? [Y/n]: y
deployment spec generated to: deployment_spec.yaml

deploying with deployment_spec.yaml...
Success!

{
│   'StackId': 'arn:aws:cloudformation:ap-south-1:213386773652:stack/test-stack/6e766f80-6992-11ec-b5ac-06ea5db619ac',
│   'StackName': 'test-stack',
│   'StackStatus': 'UPDATE_COMPLETE',
│   'CreationTime': '12/30/2021, 17:03:38',
│   'LastUpdatedTime': '01/04/2022, 16:37:14',
│   'EndpointUrl': 'https://fwxcofm8q7.execute-api.ap-south-1.amazonaws.com/Prod'
}
```

4. Check endpoint. We will try and test the endpoint The url for the endpoint given in the output of the describe command or you can also check the API Gateway through the AWS console.

    ```bash
    $ curl -i \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[[5.1, 3.5, 1.4, 0.2]]' \
      https://fwxcofm8q7.execute-api.ap-south-1.amazonaws.com/Prod/predict

    # Sample output
    HTTP/1.1 200 OK
    Content-Type: application/json
    Content-Length: 3
    Connection: keep-alive
    Date: Tue, 21 Jan 2020 22:43:17 GMT
    x-amzn-RequestId: f49d29ed-c09c-4870-b362-4cf493556cf4
    x-amz-apigw-id: GrC0AEHYPHcF3aA=
    X-Amzn-Trace-Id: Root=1-5e277e7f-e9c0e4c0796bc6f4c36af98c;Sampled=0
    X-Cache: Miss from cloudfront
    Via: 1.1 bb248e7fabd9781d3ed921f068507334.cloudfront.net (CloudFront)
    X-Amz-Cf-Pop: SFO5-C1
    X-Amz-Cf-Id: HZzIJUcEUL8aBI0KcmG35rsG-71KSOcLUNmuYR4wdRb6MZupv9IOpA==

    [0]%

5. Delete deployment
```
$ bentoctl delete -f deployment_config.yaml
```

## Quickstart with scripts

1. Build and save Bento Bundle from [BentoML quick start guide](https://github.com/bentoml/BentoML/blob/master/guides/quick-start/bentoml-quick-start-guide.ipynb)

2. Copy and change the [sample config file](lambda_config.json) given and change it according to your deployment specifications. Check out the [config section](#configuration-options) to find the differenet options.

3. Create Lambda  deployment with the deployment tool. 

   Run deploy script in the command line:

    ```bash
    $ BENTO_BUNDLE_PATH=$(bentoml get IrisClassifier:latest --print-location -q)
    $ ./deploy $BENTO_BUNDLE_PATH my-lambda-deployment lambda_config.json
    ```

   Get deployment information and status

    ```bash
    $ ./describe my-lambda-deployment

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

4. Make sample request against deployed service. The url for the endpoint given in the output of the describe command or you can also check the API Gateway through the AWS console.

    ```bash
    curl -i \
      --header "Content-Type: application/json" \
      --request POST \
      --data '[[5.1, 3.5, 1.4, 0.2]]' \
      https://j2gm5zn7z9.execute-api.us-west-1.amazonaws.com/Prod/predict

    # Sample output
    HTTP/2 200
    content-type: application/json
    content-length: 3
    date: Sat, 03 Jul 2021 19:14:38 GMT
    x-amzn-requestid: d3b5f156-0859-4f69-8b53-c60e800bc0aa
    x-amz-apigw-id: B6GLLECTSK4FY2w=
    x-amzn-trace-id: Root=1-60e0b714-18a97eb5696cec991c460213;Sampled=0
    x-cache: Miss from cloudfront
    via: 1.1 6af3b573d8970d5db2a4d03354335b85.cloudfront.net (CloudFront)
    x-amz-cf-pop: SEA19-C3
    x-amz-cf-id: ArwZ03gbs6GooNN1fy4mPOgaEpM4h4n9gz2lpLYrHmeXZJuGUJgz0Q==

    [0]%
    ```

5. Delete Lambda deployment

    ```bash
    $ ./delete my-lambda-deployment
    ```

## Configuration options

* `region`: AWS region for Lambda deployment
* `timeout`: Timeout per request
* `memory_size`: The memory for your function, set a value between 128 MB and 10,240 MB in 1-MB increments

## Deployment operations

The recommendated way to use operators is via the bentoctl CLI but you can also use this repo as standalone via the
scripts or python APIs. 

### Create a deployment

Use bentoctl

```bash
bentoctl deploy -f <deployment_config_name>
```

Use Scripts

```bash
./deploy <Bento_path> <Deployment_name> <Config_JSON default is ./lambda_config.json>
```

Use Python API

```python
from bentoctl_awslambda.deploy import deploy

deploy(BENTO_PATH, DEPLOYMENT_NAME, DEPLOYMENT_SPEC)
```

### Update a deployment

Use bentoctl

```bash
bentoctl update -f <path to deployment_config.yaml>
```

Use Scripts

```bash
./update <Bento_path> <Deployment_name> <Config_JSON>
```

Use Python API

```python
from bentoctl_awslambda.update import update
update(BENTO_PATH, DEPLOYMENT_NAME, DEPLOYMENT_SPEC)
```

### Get deployment's status and information

Use bentoctl

```bash
bentoctl describe -f <path to deployment_config.yaml>
````

Use Scripts

```bash
./describe <Deployment_name> <Config_JSON>
```

Use Python API

```python
from bentoctl_awslambda.describe import describe
describe(DEPLOYMENT_NAME, DEPLOYMENT_SPEC)
```

### Delete deployment


Use bentoctl

```bash
bentoctl update -f <path to deployment_config.yaml>
````

Use Scripts

```bash
./delete <Deployment_name> <Config_JSON>
```

Use Python API

```python
from  bentoctl_awslambda.delete import delete
delete(DEPLOYMENT_NAME, CONFIG_JSON)
```
