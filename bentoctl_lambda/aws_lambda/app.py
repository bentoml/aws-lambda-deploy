import os
import sys

from bentoml import load
from bentoml._internal.configuration.containers import DeploymentContainer
from mangum import Mangum

api_name = os.environ["BENTOML_API_NAME"]
print("loading app: ", api_name)
print("Loading from dir...")
bento_service = load("./")
print("bento service", bento_service)
# bento_service_api = bento_service.get_inference_api(api_name)

this_module = sys.modules[__name__]
# Disable /metrics endpoint since promethues is not configured for use
# in lambda
DeploymentContainer.api_server_config.metrics.enabled.set(False)
setattr(this_module, api_name, Mangum(bento_service.asgi_app))
