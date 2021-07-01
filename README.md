# aws-lambda-deploy
Deploy BentoML models to AWS Lambda

### Deployment

Deploy to AWS Lambda.
```bash
python deploy.py <path to bentoml bundle> <deployment name> <path to
config_json>
```

### Updating

Update a deployment with either a new Image or API. The `deploy` command also
has the same functionality as update. This is because we use the SAM cli which
automatically takes care of finding the changes and updating the AWS
Cloudformations stack. Make sure you give the same *`<deployment name>`* you
gave when calling the `deploy` command.

```bash
python deploy.py <path to bentoml bundle> <deployment name> <path to
config_json>
```
