from .delete import delete
from .deploy import deploy
from .describe import describe
from .update import update

OPERATOR_NAME = "aws-lambda"
OPERATOR_SCHEMA = {
    "region": {"required": True, "type": "string", "default": "us-west-1"},
    "timeout": {"required": False, "type": "integer", "coerce": int, "default": 10},
    "memory_size": {
        "required": False,
        "type": "integer",
        "coerce": int,
        "default": 512,
    },
}
