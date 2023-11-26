
"""
This is the primary FastAPI router where LLM endpoints are proxied and monitored.

This is a barebones sagemaker POC and further development is required to use.

"""
# pylint: disable=too-many-locals,too-many-arguments,dangerous-default-value
import datetime
import json
import os
import uuid
import requests

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from src.constants import CONTENT_TYPE, ENABLE_SUBM_API, LLM_TYPE, SAGEMAKER, URL
from src.modules.common import RequestException, log_to_esentire
from src.modules.database import get_db, uuid_exists
from src.modules.logger import logger
from src.modules.auto_models import ChatgptLog
from src.modules.classes import (
    ChatSagemakerJson,
    unknown_error,
    chat_success,
    scope_error,
    dns_error,
)

sgmaker_router = APIRouter()

# Only display this endpoint if sagemaker is enabled
if SAGEMAKER in LLM_TYPE:

    # LLM endpoints proxied to in this API
    @sgmaker_router.post(
        "/chat_sg",
        tags=["Sagemaker"],
        responses={200: chat_success, 400: unknown_error, 500: dns_error, 403: scope_error},
    )
    async def submit_chat_sg(
        json_object: ChatSagemakerJson,
        db_engine: Session = Depends(get_db),
    ):
        """
        This is the primary endpoint used to send that proxies business user interactions to an LLM.
        """
        # pylint: disable=protected-access
        json_object = json_object.dict(exclude_unset=True)

        json_object["inputs"] = [json_object["inputs"]]

        logger.info("json_object: %s", json_object)
        # Pass on the related authorization key to the llm
        headers = {
            "Content-Type": CONTENT_TYPE
        }

        # This generates a uuid to track each record in the db
        while True:
            uuid_generated = uuid.uuid4()
            if uuid_exists(uuid_generated, db_engine):
                continue
            break

        
        try:
            time_submitted = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            # Send a POST request to the API endpoint
            response = requests.post(URL, headers=headers, json=json_object, timeout=60)
            
            logger.info("Configuration of request: %s", json_object)
            logger.info("Response: %s", response.json())
            # logger.info("Usage stats: %s", response.json()["usage"])

            response_json = response.json()

            chat_log = ChatgptLog(
                id=uuid_generated,
                request=json.dumps(json_object),
                response=json.dumps(response.json()),
                #usage_info=json.dumps(response.json()["usage"]),
                user_name = "user", # Replace with the actual username of whomever sent the request using whichever IAM tools you prefer
                title = "tile", # Replace with title-- this is an example of additional metadata that might be useful to capture, or to use in your dashboards to create interesting job role based reports
                convo_title="no title", # This is used in the chat history feature so users can quickly get an idea of prior conversation content
                root_gpt_id= "1" # This is used to draw a lineage between different interactions so we can trace a single conversation
            )

            # Store this primary
            db_engine.add(chat_log)
            db_engine.commit()

            if ENABLE_SUBM_API=="true":
                try:
                    print("logging to esentire")
                    esentire_response = log_to_esentire(
                        raw_request=json_object,
                        raw_response=response.json(),
                        associated_users= ["example_user_id"],
                        time_submitted= time_submitted,
                        associated_devices= ["device1, device2"],
                        associated_software= ["software1","software2"]
                        )
                except Exception as error:
                    print("Error logging to esentire in submit_chat: {error}")
                    
            # Return the generated text as a response to the client
            return response.json()

        except requests.exceptions.RequestException as error:
            # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
            raise RequestException(
                status_code=500,
                msg="Could not connect to ChatGPT API, error context: {error}",
            ) from error

        except Exception as error:
            raise RequestException(
                status_code=400, msg=f"something went wrong: {error}"
            ) from error
