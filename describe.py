import sys


def describe_lambda_deployment(deployment_name):
    pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Please provide deployment name")
    deployment_name = sys.argv[1]

    describe_lambda_deployment(deployment_name)
