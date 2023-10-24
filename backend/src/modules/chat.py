"""
This is the primary FastAPI router where LLM endpoints are proxied and monitored.
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

from src.modules.common import RequestException, log_to_esentire
from src.modules.database import get_db, uuid_exists
from src.modules.logger import logger
from src.modules.auto_models import ChatgptLog, ImageLog, MetaSummarizerLog
from src.modules.classes import (
    ChatJson,
    CheckChatJson,
    TitleUpdateJson,
    RootUuidJson,
    ImgJson,
    unknown_error,
    chat_success,
    img_gen_resp,
    remove_convo,
    history_v2,
    history,
    title_updated,
    missing_item,
    timeout_error,
    scope_error,
    dns_error,
)


chat_router = APIRouter()

# LLM endpoints proxied to in this API
URL = os.environ["LLM_ENDPOINT"]
URL_IMAGE = os.environ["LLM_IMG_ENDPOINT"]

@chat_router.post(
    "/chat",
    tags=["ChatGPT"],
    responses={200: chat_success, 400: unknown_error, 500: dns_error, 403: scope_error},
)
async def submit_chat(
    json_object: ChatJson,
    db_engine: Session = Depends(get_db),
):
    """
    This is the primary endpoint used to send that proxies business user interactions to an LLM.
    """
    # pylint: disable=protected-access
    json_object = json_object.dict(exclude_unset=True)
    # Pass on the related authorization key to the llm
    headers = {
        "Content-Type": os.environ["LLM_API_CONTENT_TYPE"],
        "Authorization": os.environ["LLM_API_AUTHORIZATION"]
    }

    # This generates a uuid to track each record in the db
    while True:
        uuid_generated = uuid.uuid4()
        if uuid_exists(uuid_generated, db_engine):
            continue
        break

    # Extract the convo_title if passed alongside request, so we don't pass downstream to llm, since this is an internal field
    convo_title=""
    if "convo_title" in json_object:
        convo_title = json_object.pop("convo_title")
    else:
        convo_title = json_object["messages"][0]["content"][:50]

    # Extract the root_id if passed alongside request, so we don't pass downstream to llm, since this is an internal field
    gpt_root_id= None
    if "root_id" in json_object:
        gpt_root_id = json_object.pop("root_id")


    logger.info("uuid: %s", uuid_generated)
    logger.info("convo_title: %s", convo_title)
    
    try:
        time_submitted = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # Send a POST request to the API endpoint
        response = requests.post(URL, headers=headers, json=json_object, timeout=60)
        
        logger.info("Configuration of request: %s", json_object)
        logger.info("Response: %s", response.json()["choices"][0]["message"]["content"])
        logger.info("Usage stats: %s", response.json()["usage"])

        response_json = response.json()
        response_json.update({"uuid": str(uuid_generated)})

        if gpt_root_id == None:
            gpt_root_id = response_json.get('id')

        chat_log = ChatgptLog(
            id=uuid_generated,
            request=json.dumps(json_object),
            response=json.dumps(response.json()),
            usage_info=json.dumps(response.json()["usage"]),
            user_name = "user", # Replace with the actual username of whomever sent the request using whichever IAM tools you prefer
            title = "title", # Replace with title-- this is an example of additional metadata that might be useful to capture, or to use in your dashboards to create interesting job role based reports
            convo_title=convo_title, # This is used in the chat history feature so users can quickly get an idea of prior conversation content
            root_gpt_id= gpt_root_id # This is used to draw a lineage between different interactions so we can trace a single conversation
        )

        # Store this primary
        db_engine.add(chat_log)
        db_engine.commit()

        if os.environ["ENABLE_SUBMISSIONS_API"]=="true":
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

# 
@chat_router.post(
    "/checkchat",
    tags=["ChatGPT"],
    responses={
        200: chat_success,
        400: unknown_error,
        500: dns_error,
        403: scope_error,
        404: missing_item,
        504: timeout_error,
    },
)
async def submit_chat_check(
    json_object: CheckChatJson,
    db_engine: Session = Depends(get_db),
):
    """
    Passing chat prompt to db to check if exists.
    This is a work around in one of our early prototypes: Using aws api gateway, the /chat endpoints sometimes 
    exceeded 30 seconds to return a response to the user, resulting in the AWS gateway 504 timed out response.
    Since each interaction is stored in the database, this endpoint is used to query the database to retrieve the response
    rather than to resubmit another call to the LLM using the /chat endpoint.

    If you use this, take care as it could result in users accessing data of other users. Make sure to modify this so a user may only pull records for themselves.
    """
    # pylint: disable=import-outside-toplevel
    import datetime

    json_object = json_object.dict(exclude_unset=True)
    current_time = datetime.datetime.utcnow()  # Get the current time utc

    logger.info("current utc time: %s", str(current_time))
    logger.info("json object to search: %s", json.dumps(json_object))
    try:
        chat_log = ( 
            db_engine.query(ChatgptLog)
            .filter(
                ChatgptLog.request == json.dumps(json_object),
                ChatgptLog.response_time
                >= current_time - datetime.timedelta(minutes=15),
            )
            .order_by(ChatgptLog.response_time.desc())
            .first()
        )
        

        # Return the generated text as a response to the client
        return chat_log.response

    except requests.exceptions.RequestException as error:
        # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
        raise RequestException(
            status_code=500,
            msg=f"Could not connect to ChatGPT API, error context: {error}",
        ) from error

    except AttributeError as error:
        raise RequestException(
            status_code=404,
            msg=f"Unable to find the given request, try polling again or contact dev team \
                if you made the request greater than 15 minutes ago. Details: {error}", 
        ) from error

    except Exception as error:
        raise RequestException(
            status_code=400, msg=f"something went wrong: {error}"
        ) from error

@chat_router.post(
    "/update_title",
    tags=["ChatGPT"],
    responses={
        200: title_updated,
        400: unknown_error,
        500: dns_error,
        403: scope_error,
        504: timeout_error,
    },
)
async def submit_title_update(
    json_object: TitleUpdateJson,
    db_engine: Session = Depends(get_db),
):
    """
    Updating a title for a openai chat
    This is a database utitility endpoint to allow users/apps to modify the title of a conversation (a series of rows in the database sharing the same root uuid)
    """
    # pylint: disable=line-too-long
    json_object = json_object.dict(exclude_unset=True)
    try:
        db_engine.query(ChatgptLog).filter(
            ChatgptLog.root_gpt_id == json_object["root_id"],
        ).update({"convo_title": json_object["convo_title"]})
        db_engine.commit()

        # Return the generated text as a response to the client
        return {
            "message": "Successfully updated the titles!",
            "new_title": json_object["convo_title"],
        }

    except requests.exceptions.RequestException as error:
        # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
        raise RequestException(
            status_code=500,
            msg=f"Could not connect to ChatGPT API, error context: {error}",
        ) from error

    except AttributeError as error:
        raise RequestException(
            status_code=404,
            msg=f"Unable to find the given request, try polling again or contact dev team \
                if you made the request greater than 15 minutes ago. Details: {error}",
        ) from error

    except Exception as error:
        raise RequestException(
            status_code=400, msg=f"something went wrong: {error}"
        ) from error


@chat_router.post(
    "/update_title_openai",
    tags=["ChatGPT"],
    responses={
        200: title_updated,
        400: unknown_error,
        500: dns_error,
        403: scope_error,
        504: timeout_error,
    },
)
async def submit_title_update_openai_experimental(
    json_object: RootUuidJson,
    db_engine: Session = Depends(get_db),
):
    """
    updating a title for an openai chat but use openai to update the title
    """
    # pylint: disable=line-too-long
    json_object = json_object.dict(exclude_unset=True)

    headers = {
        "Content-Type": os.environ["LLM_API_CONTENT_TYPE"],
        "Authorization": os.environ["LLM_API_AUTHORIZATION"],
    }
    
    while True:
        uuid_generated = uuid.uuid4()
        if uuid_exists(uuid_generated, db_engine):
            continue
        break
    try:
        chat_log = (
            db_engine.query(ChatgptLog.request)
            .filter(
                ChatgptLog.root_gpt_id == json_object["root_id"],
            )
            .order_by(ChatgptLog.response_time.desc())
            .first()
        )

        if chat_log == None:
            raise Exception("No records found for this root_gpt_id.")
                
        logger.info("chat_log: %s", chat_log)

        user_messages = []
        chat_log_dict = json.loads(chat_log[0])
        for message in chat_log_dict["messages"]:
            if message["role"] == "user":
                user_messages.append(message["content"])
        prompt = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a conversation summerizer, you will sumerize a conversation for a list of user requests to openai. Output should be a summerization that has a max of 49 characters and avoid mentioning the user.",
                },
                {"role": "user", "content": f"conversation: {user_messages}"},
            ],
        }

        response = requests.post(URL, headers=headers, json=prompt, timeout=60)

        logger.info("Configuration of request: %s", prompt)
        logger.info("Response: %s", response.json()["choices"][0]["message"]["content"])
        logger.info("Usage stats: %s", response.json()["usage"])

        chat_log = ChatgptLog(
            id=uuid_generated,
            request=json.dumps(prompt),
            response=json.dumps(response.json()),
            usage_info=json.dumps(response.json()["usage"]),
            user_name="user",
            title="title",
            convo_title="summarizer",
            convo_show=False,
        )

        db_engine.add(chat_log)
        db_engine.commit()

        chat_log = (
            db_engine.query(ChatgptLog)
            .filter(
                ChatgptLog.root_gpt_id == json_object["root_id"],
            )
            .update(
                {"convo_title": response.json()["choices"][0]["message"]["content"]}
            )
        )

        db_engine.commit()

        # Return the generated text as a response to the client
        # return response.json()["choices"][0]["message"]["content"]
        return {
            "message": "Successfully updated the titles!",
            "new title": response.json()["choices"][0]["message"]["content"],
        }

    except requests.exceptions.RequestException as error:
        # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
        raise RequestException(
            status_code=500,
            msg=f"Could not connect to ChatGPT API, error context: {error}",
        ) from error

    except AttributeError as error:
        raise RequestException(
            status_code=404,
            msg=f"Unable to find the given request, try polling again or contact dev team \
                if you made the request greater than 15 minutes ago. Details: {error}",
        ) from error

    except Exception as error:
        raise RequestException(
            status_code=400, msg=f"something went wrong: {error}"
        ) from error


@chat_router.post(
    "/metadata_check",
    tags=["ChatGPT"],
    responses={
        200: title_updated,
        400: unknown_error,
        500: dns_error,
        403: scope_error,
        504: timeout_error,
    },
)
async def submit_metadata_query_experimental(
    json_object: RootUuidJson,
    db_engine: Session = Depends(get_db),
):
    """
    Meta data check for a given chat. 
    Use open ai to derive additional metadata on existing interactions.
    Pass the root_gpt_id so that you can get the entire conversation context.
    Only the most recent interaction with the entire conversation history is summarized.
    """
    # pylint: disable=line-too-long
    json_object = json_object.dict(exclude_unset=True)

    headers = {
        "Content-Type": os.environ["LLM_API_CONTENT_TYPE"],
        "Authorization": os.environ["LLM_API_AUTHORIZATION"] ,
    }
    
    while True:
        uuid_generated = uuid.uuid4()
        if uuid_exists(uuid_generated, db_engine):
            continue
        break
    try:
        chat_log = (
            db_engine.query(ChatgptLog)
            .filter(
                ChatgptLog.root_gpt_id == json_object["root_id"],
            )
            .order_by(ChatgptLog.response_time.desc())
            .first()
        )
        prompt = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": """I will provide a JSON object describing a previous conversation with an LLM assistant, along with details about the job title of the user having the conversation.  You will analyze the conversation and extract data points about the conversation in machine readable format, expressing your responses only as JSON.  You will output only a JSON structure similar to the following, with values assessed from the conversation I pass you and comments removed, no other text.  Your response will be loaded directly into a DB, so ONLY output the JSON structure and nothing else.  Here is an example JSON for reference with comments.

{
  "chat_summary": "Creative Writing", // This key should contain a succinct summary of why you think the human was having the conversation with an LLM.  
  "description": "The assistant helped write a horror story" // This key should contain a more detailed summarized description of the key deliverables provided by the LLM assistant to the user.
  "llm_deliverables": ["Sample Paragraphs, Source Code, Research"] // This key should contain an array of all the deliverables produced by the assistant for the user.
  "satisfaction_score": "0.76" // This key should express as a percentage how satisfied the user appears to be with the final LLM response on a scale from 0 to 1. 1 indicates very satisfied, 0 indicates the user wasted time and did not get what they wanted. Only assess the user messages for this key, not the assistant messages.
  "work_related": "true", // This key should simply provide a boolean value as to whether or not the conversation appeared to be work related.
  "user_seconds_saved": "120", // This key should provide a time estimate, in seconds, of how much total time you think the assistant was able to save the human given the context provided. 
  "assistant_seconds_saved: "80", //  Assuming the assistant was also a human, estimate in seconds how much total time it would have taken a human assistant to formulate and draft the responses in the conversation, assuming they had the domain knowledge to produce the deliverables.
  assistant_wage: "21.50", // Assuming the assistant was a human, estimate the hourly fully loaded employee cost in 2021 US dollars to pay a competent human assistant to deliver the responses in this conversation.
"languages": "English", // This key should return a list of all natural languages used by either the human or the LLM, such as French, and also programming languages such as Python.
}""",
                },
                {
                    "role": "user",
                    "content": f"{{user_title: {chat_log.title}, conversation: {chat_log.request} }}",
                },
            ],
        }

        response = requests.post(URL, headers=headers, json=prompt, timeout=60)

        logger.info("Configuration of request: %s", prompt)
        logger.info("Response: %s", response.json()["choices"][0]["message"]["content"])
        logger.info("Usage stats: %s", response.json()["usage"])

        summarized_log = MetaSummarizerLog(
            id=uuid_generated,
            request=json.dumps(prompt),
            response=json.dumps(response.json()),
            usage_info=json.dumps(response.json()["usage"]),
            user_name="user",
            title="title",
            orig_summarized_id=chat_log.id,
        )

        db_engine.add(summarized_log)
        db_engine.commit()

        return {
            "message": "Here is your blob",
            "metadata": response.json()["choices"][0]["message"]["content"],
        }

    except requests.exceptions.RequestException as error:
        # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
        raise RequestException(
            status_code=500,
            msg=f"Could not connect to ChatGPT API, error context: {error}",
        ) from error

    except AttributeError as error:
        raise RequestException(
            status_code=404,
            msg=f"Unable to find the given request, try polling again or contact dev team \
                if you made the request greater than 15 minutes ago. Details: {error}",
        ) from error

    except Exception as error:
        raise RequestException(
            status_code=400, msg=f"something went wrong: {error}"
        ) from error


@chat_router.get(
    "/history",
    tags=["ChatGPT"],
    responses={
        200: history,
        400: unknown_error,
        500: dns_error,
        403: scope_error,
        504: timeout_error,
    },
)
async def check_history(
    db_engine: Session = Depends(get_db),
):
    """
    Retrieve ALL records of llm interactions for a specific user.
    This endpoint should be modified to check the history of the authenticated user.
    """
    
    try:
        chat_log = (
            db_engine.query(ChatgptLog.request, ChatgptLog.response_time)
            .distinct()
            .filter(
                ChatgptLog.user_name == "user",
                ChatgptLog.title == "title",
            )
            .order_by(ChatgptLog.response_time.desc())
            .all()
        )

        # Return the generated text as a response to the client
        return {"Historical_list": chat_log}

    except requests.exceptions.RequestException as error:
        # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
        raise RequestException(
            status_code=500,
            msg=f"Could not connect to ChatGPT API, error context: {error}",
        ) from error

    except Exception as error:
        raise RequestException(
            status_code=400, msg=f"something went wrong: {error}"
        ) from error


@chat_router.get(
    "/history_v2",
    tags=["ChatGPT"],
    responses={
        200: history_v2,
        400: unknown_error,
        500: dns_error,
        403: scope_error,
        504: timeout_error,
    },
)
async def check_history_v2(
    db_engine: Session = Depends(get_db),
):
    """
    Check history of the user, uses root_gpt_ids, only showing most recent ones.
    This endpoint should be modified to check the history of the authenticated user.
    """
    
    try:
        query = db_engine.query(
                        ChatgptLog
                    ).filter(
                        ChatgptLog.user_name == 'user',
                        ChatgptLog.root_gpt_id.isnot(None),
                        ChatgptLog.convo_show == True
                    ).order_by(
                        ChatgptLog.root_gpt_id,
                        ChatgptLog.response_time.desc()
                    ).distinct(
                        ChatgptLog.root_gpt_id)
        #Make sure to replace user_name and title vars containing actual user name and title
        chat_log = query.all()
        logger.info("chat log complete")
        # Return the generated text as a response to the client
        return {"Historical_Conversations": chat_log}

    except requests.exceptions.RequestException as error:
        # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
        raise RequestException(
            status_code=500,
            msg=f"Could not connect to ChatGPT API, error context: {error}",
        ) from error

    except Exception as error:
        raise RequestException(
            status_code=400, msg=f"something went wrong: {error}"
        ) from error


@chat_router.post(
    "/remove_convo",
    tags=["ChatGPT"],
    responses={
        200: remove_convo,
        400: unknown_error,
        500: dns_error,
        403: scope_error,
        504: timeout_error,
    },
)
async def submit_visibility_update(
    json_object: RootUuidJson,
    db_engine: Session = Depends(get_db),
):
    """
    deleting conversation visibility for an openai chat
    """
    # pylint: disable=line-too-long
    json_object = json_object.dict(exclude_unset=True)
    
    try:
        db_engine.query(ChatgptLog).filter(
            ChatgptLog.root_gpt_id == json_object["root_id"],
        ).update({"convo_show": False})
        db_engine.commit()

        # Return the generated text as a response to the client
        return {"message": "Successfully updated the convo visibility!"}

    except requests.exceptions.RequestException as error:
        # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
        raise RequestException(
            status_code=500,
            msg=f"Could not connect to ChatGPT API, error context: {error}",
        ) from error

    except AttributeError as error:
        raise RequestException(
            status_code=404,
            msg=f"Unable to find the given request, try polling again or contact dev team \
                if you made the request greater than 15 minutes ago. Details: {error}",
        ) from error

    except Exception as error:
        raise RequestException(
            status_code=400, msg=f"something went wrong: {error}"
        ) from error


@chat_router.post(
    "/image_gen",
    tags=["ChatGPT"],
    responses={
        200: img_gen_resp,
        400: unknown_error,
        500: dns_error,
        403: scope_error,
        504: timeout_error,
    },
)
async def image_gen(
    json_object: ImgJson,
    db_engine: Session = Depends(get_db),
):
    """
    Generate an image
    """
    json_object = json_object.dict(exclude_unset=True)
    
    headers = {
        "Content-Type": os.environ["LLM_API_CONTENT_TYPE"],
        "Authorization": os.environ["LLM_API_AUTHORIZATION"] ,
    }
    

    size = json_object["size"]
    if size == "1024x1024":
        cost_per_image = 0.020
    elif size == "512x512":
        cost_per_image = 0.018
    elif size == "256x256":
        cost_per_image = 0.016
    else:
        raise RequestException(status_code=400, msg="Image size is incorrect")
    number_images = json_object["n"]
    total_cost = number_images * cost_per_image

    
    try:
        time_submitted = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # Send a POST request to the API endpoint
        response = requests.post(
            URL_IMAGE, headers=headers, json=json_object, timeout=60
        )
        full_response = json.dumps(response.json())

        logger.info("Configuration of request: %s", json_object)
        logger.info("Response: %s", json.dumps(response.json()))
        logger.info("Usage costs: %s", total_cost)

        image_log = ImageLog(
            request=json.dumps(json_object),
            response=full_response,
            usage_cost=total_cost,
            user_name="user",
            title="title",
        )

        db_engine.add(image_log)
        db_engine.commit()


        if os.environ["ENABLE_SUBMISSIONS_API"]:
            try:
                esentire_response = log_to_esentire(
                    raw_request=json_object,
                    raw_response=response.json(),
                    associated_users= ["example_user_id"],
                    time_submitted= time_submitted,
                    associated_devices= ["device1, device2"],
                    associated_software= ["software1","software2"]
                    )
            except Exception as error:
                print("Error logging to esentire in image_gen: {error}")

        # Return the generated text as a response to the client
        return response.json()

    except requests.exceptions.RequestException as error:
        # Handle network errors (e.g. DNS resolution failure, connection timeout, etc.)
        raise RequestException(
            status_code=500,
            msg=f"Could not connect to ChatGPT API, error context: {error}",
        ) from error

    except Exception as error:
        raise RequestException(
            status_code=400, msg=f"something went wrong: {error}"
        ) from error
