import os
import sys

from bentoml import load
from mangum import Mangum

api_name = os.environ["BENTOML_API_NAME"]
print("loading app: ", api_name)
print("Loading from dir...")
bento_service = load("./")
print("bento service", bento_service)
# bento_service_api = bento_service.get_inference_api(api_name)

this_module = sys.modules[__name__]
setattr(this_module, api_name, Mangum(bento_service.asgi_app))
