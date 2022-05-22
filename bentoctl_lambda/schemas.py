OPERATOR_SCHEMA = {
    "region": {
        "required": True,
        "type": "string",
        "default": "us-west-1",
        "help_message": "AWS region for Lambda deployment",
    },
    "timeout": {
        "required": False,
        "type": "integer",
        "coerce": int,
        "default": 10,
        "help_message": "Timeout per request",
    },
    "memory_size": {
        "required": False,
        "type": "integer",
        "coerce": int,
        "default": 512,
        "help_message": "The memory for your function, set a value between 128 MB and 10,240 MB in 1-MB increments",
    },
}

other_schema = {
    "deployment_name": {
        "required": True,
        "type": "string",
        "help_message": "Deployment Name",
    }
}

# merge both dicts
PARAMETER_SCHEMA = {**OPERATOR_SCHEMA, **other_schema}
