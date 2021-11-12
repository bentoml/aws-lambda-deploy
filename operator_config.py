OPERATOR_NAME = "aws-lambda"

OPERATOR_MODULE = "awslambda"

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
