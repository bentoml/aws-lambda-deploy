import os

from bentoml import load
from bentoml._internal.configuration.containers import DeploymentContainer
from mangum import Mangum

API_GATEWAY_STAGE = os.environ.get('API_GATEWAY_STAGE', None)
print("Loading from dir...")
bento_service = load("./")
print("bento service", bento_service)

# Disable /metrics endpoint since promethues is not configured for use
# in lambda
DeploymentContainer.api_server_config.metrics.enabled.set(False)
mangum_app = Mangum(bento_service.asgi_app, api_gateway_base_path=API_GATEWAY_STAGE)
