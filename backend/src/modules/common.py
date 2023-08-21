"""
common utility functions for this api
"""
import datetime
import json
import requests
import os

LLM_PROVIDER_LIST = ["OPEN_AI", "GOOGLE", "HUGGING_FACE", "META", "[INSERT YOUR MODEL PROVIDER]"]

class RequestException(Exception):
    """
    request exception class
    """

    def __init__(self, msg: str, status_code: int):
        super().__init__()
        self.msg = msg
        self.status_code = status_code

def log_to_esentire(raw_request:json, raw_response:json, associated_users:list, time_submitted: datetime, associated_devices:list, associated_software:list):
    required_data = {
        "raw_request": raw_request,
        "raw_response": raw_response,
        "associated_users": associated_users,
        "time_submitted": time_submitted, 
        "time_logged": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "response_timestamp": datetime.datetime.fromtimestamp(raw_response["created"]).strftime("%Y-%m-%dT%H:%M:%S"),
        "llm_model": raw_request["model"],
        "llm_provider": LLM_PROVIDER_LIST[0], #Index your relevant provider. If not present, update the array with your provider
        "associated_devices": associated_devices,
        "associated_software": associated_software,
        "api_token_id": "example_token_id"
    }

    sub_response = ""
    try:
        sub_response = requests.post(os.environ["SUBMISSIONS_API_URL"], json=required_data, timeout=60)
        print(f"Success logging: {sub_response.text}")
    except Exception as error:
        print(f"Error logging to esentire at log_to_esentire: {error}")

    return sub_response