# aws-lambda-deploy
Deploy BentoML models to AWS Lambda

### Deployment

Deploy to AWS Lambda.
```bash
python deploy.py <path to bentoml bundle> <deployment name> <path to
config_json:optional>
```

### Updating

Update a deployment with either a new Image or API. The `deploy` command also
has the same functionality as update. This is because we use the SAM cli which
automatically takes care of finding the changes and updating the AWS
Cloudformations stack. Make sure you give the same *`<deployment name>`* you
gave when calling the `deploy` command.

```bash
python update.py <path to bentoml bundle> <deployment name> <path to
config_json:optional>
```


### Deleting

To delete the stack from AWS, simply run the `delete.py` file with the correct
*`<deployment name>`*. This will remove the ECR registry and the Cloudformations
stack.

```
python delete.py <deployment name> <path to config_json: optional>
```

### Describe

Show information about the lambda deployment.

```bash
python describe.py <deployment name>
```
