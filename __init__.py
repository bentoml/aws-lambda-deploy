from deploy import deploy
from update import update
from describe import describe
from delete import delete

OPERATOR_NAME = "aws-lambda"
DEFAULT_FIELDS = {"timeout": 10, "max_memory": 512}
REQUIRED_FIELDS = ["region"]
