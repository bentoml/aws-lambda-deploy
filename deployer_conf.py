"""
aws-lambda-deployer deploys the given bento bundle to the Lambda service provided by
AWS. AWS Lambda is a perfect option is you want to deploy only the models in a
serverless fashion.
"""
from deploy import deploy
from delete import delete
from describe import describe
from update import update


name = "aws-lambda-deployer"

default_config = {"region": None, "timeout": 60, "memory": 512}
