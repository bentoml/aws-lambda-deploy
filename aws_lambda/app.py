from bentoml.saved_bundle import load_from_dir
import logging
import os
import sys


# bento_name = os.environ['BENTOML_BENTO_SERVICE_NAME']
# api_name = os.environ["BENTOML_API_NAME"]
api_name = os.environ["BENTOML_API_NAME"]


print('loading app: ', api_name)
this_module = sys.modules[__name__]

def api_func(event, context):
    print('Loading from dir...')
    bento_service = load_from_dir('./')
    service_api = bento_service.get_inference_api(api_name)
    print('loaded API: ', service_api.name)

    print('Event: ', event)
    prediction = service_api.handle_aws_lambda_event(event)
    print(prediction['body'], prediction['statusCode'])
    return prediction


setattr(this_module, api_name, api_func)
