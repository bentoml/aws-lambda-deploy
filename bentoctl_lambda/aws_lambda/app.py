import os

from bentoml import load
from mangum import Mangum

API_GATEWAY_STAGE = os.environ.get("API_GATEWAY_STAGE", None)

print("Loading from dir...")
bento_service = load("./", standalone_load=True)

print("bento service", bento_service)

mangum_app = Mangum(bento_service.asgi_app, api_gateway_base_path=API_GATEWAY_STAGE)
