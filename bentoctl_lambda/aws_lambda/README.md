AWS Lambda supports deployment via containers of upto 10gb and that is what we
are using for deploying bentos into lambda. The docs can be accessed
[here](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html).

In order for AWS to run the container in lambda they require the following
- Defining a handler: this is the python code that will handle the `event` and
  `context` dict that is passed when ever the lambda function is invoked. Our
  handler is defined in ./app.py and it uses
  [Mangum](https://github.com/jordaneremieff/mangum) to handle the incoming
  requrest. 
- setup aws-lambda-ric: this is the runtime-interface-client that AWS has
  developed to interface with the Runtime API
  (https://github.com/aws/aws-lambda-python-runtime-interface-client). The
  ./entry_script.sh handles invoking and loading the handler with the RIC.

## Terraform setup

AWS lambda is setup with an HTTP API infront to act as public endpoint for the
lambda function. Any request that comes is passed onto the lambda function. The
request is handled by mangum which transforms it into a ASGI request that can be
processed by bentoml's ASGI app. 

All the logs are in cloudwatch and IAM policies for every infra is created by
the terraform template.

## Dev setup

Right now running it locally is not possible. There is a lambda Runtime Emulator
that loads any handler and emulates the AWS interface but it is still work in
progress.
