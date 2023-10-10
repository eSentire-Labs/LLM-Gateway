"""
This is the primary FastAPI router where LLM endpoints are proxied and monitored.

This is a barebones sagemaker POC and further development is required to use.

"""
# pylint: disable=line-too-long,too-few-public-methods,no-name-in-module
from typing import Optional, Any, List
from pydantic import BaseModel, Field, Json

class ChatJson(BaseModel):
    """
    ChatGPT chat endpoint expected json input styling
    """

    inputs: List[dict] = Field(
        ...,
        description="list of messages with roles associated",
        example="""[{"role": "user", "content": "Hello!"}]""",
    )
    parameters: dict = Field(
        description="kwargs for the llama model. See more here: https://huggingface.co/docs/transformers/main_classes/text_generation#transformers.GenerationConfig",
        example= {
		"max_new_tokens": 512,
		"top_p": 0.9,
		"temperature": 0.6
	    }
    )
    root_id: Optional[str] = Field(
        None,
        description="The root UUID of the conversation, if applicable. This is how you connect conversations",
    )
    convo_title: Optional[str] = Field(
        None,
        description="The title of the conversation, if applicable. This is needed if you change convo titles",
    )

class CheckChatJson(BaseModel):
    """
    ChatGPT chat endpoint expected json input styling
    """

    model: str = Field(
        ...,
        description="The name of the model you want to use",
        example="gpt-3.5-turbo",
    )
    messages: list = Field(
        ...,
        description="list of messages with roles associated",
        example="""[{"role": "user", "content": "Hello!"}]""",
    )

class TitleUpdateJson(BaseModel):
    """
    ChatGPT title update json input styling
    """

    root_id: str = Field(
        None,
        description="The root UUID of the conversation, if applicable. This is how you connect conversations",
        example="""xxxxxxxx-xx-xxxx-xxxx-xxxxxx""",
    )
    convo_title: str = Field(
        None,
        description="The title of the conversation, if applicable. This is needed if you change convo titles",
        example="""new title""",
    )


class RootUuidJson(BaseModel):
    """
    ChatGPT json input styling which only expects a root_id
    """

    root_id: str = Field(
        None,
        description="The root UUID of the conversation, if applicable. This is how you connect conversations",
        example="""xxxxxxxx-xx-xxxx-xxxx-xxxxxx""",
    )


class ImgJson(BaseModel):
    """
    ChatGPT image json input styling
    """

    prompt: str = Field(
        ..., description="Prompt for image generation", example="A cute baby sea otter"
    )
    n: int = Field(..., description="How many images you want generated", example=2)
    size: str = Field(
        ...,
        description="size of the image you want, three are available: 1024x1024, 512x512, 256x256",
        example="1024x1024",
    )


unknown_error = {
    "description": "Unknown error",
    "content": {
        "application/json": {"example": {"msg": "something went wrong: {error}"}}
    },
}

chat_success = {
    "description": "Success",
    "content": {
        "application/json": {
            "example": {
                "id": "chatcmpl-id",
                "object": "chat.completion",
                "created": 1682456485,
                "model": "gpt-3.5-turbo-0301",
                "usage": {
                    "prompt_tokens": 90,
                    "completion_tokens": 46,
                    "total_tokens": 136,
                },
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Response"},
                        "finish_reason": "stop",
                        "index": 0,
                    }
                ],
                "root_uuid": "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxx"
            }
        }
    },
}

dns_error = {
    "description": "DNS Failure",
    "content": {
        "application/json": {
            "example": {
                "msg": "Could not connect to ChatGPT API, error context: {error}"
            }
        }
    },
}

scope_error = {
    "description": "User does not have needed scope",
    "content": {
        "application/json": {
            "example": {"msg": "Required scope for this function not found"}
        }
    },
}

timeout_error = {
    "description": "User does not have needed scope",
    "content": {
        "application/json": {
            "example": {"msg": "The operation timed out. Please try again later."}
        }
    },
}

missing_item = {
    "description": "Item requested could not be found",
    "content": {
        "application/json": {
            "example": {
                "msg": "Unable to find the given request, try polling again or contact dev team \
                if you made the request greater than 15 minutes ago."
            }
        }
    },
}

title_updated = {
    "description": "Title has been updated",
    "content": {
        "application/json": {
            "example": {
                "message": "Successfully updated the titles!",
                "new_title": "{title}",
            }
        }
    },
}

history = {
    "description": "History of requests",
    "content": {
        "application/json": {"example": {"Historical_list": "[{historical list}]"}}
    },
}

history_v2 = {
    "description": "History of requests version 2",
    "content": {
        "application/json": {
            "example": {"Historical_Conversations": "[{historical conversations}]"}
        }
    },
}

remove_convo = {
    "description": "remove a convorsation from being visible",
    "content": {
        "application/json": {
            "example": {"message": "Successfully updated the convo visibility!"}
        }
    },
}

img_gen_resp = {
    "description": "remove a convorsation from being visible",
    "content": {
        "application/json": {
            "example": {"data": [{"url": "{url}"}], "created": 1681841990}
        }
    },
}
