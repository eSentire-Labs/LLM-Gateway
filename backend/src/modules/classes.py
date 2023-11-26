"""
ChatGPT related classes and response variables
"""
# pylint: disable=line-too-long,too-few-public-methods,no-name-in-module
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatJson(BaseModel):
    """
    Open AI completion endpoint expected json input styling
    """

    model: str = Field(
        ..., # Pydantic notation for a required Field https://docs.pydantic.dev/dev/concepts/models/#required-fields
        description="(Required if Open AI) The name of the model you want to use",
        example="gpt-3.5-turbo",
    )
    messages: list = Field(
        ...,
        description="(Required if Open AI) List of messages with roles associated",
        example="""[{"role": "user", "content": "Hello!"}]""",
    )
    messages: Optional[list] = Field(
        ...,
        description="(Required if Open AI) List of messages with roles associated",
        example="""[{"role": "user", "content": "Hello!"}]""",
    )
    root_id: str = Field(
        None,
        description="The root UUID of the conversation, if applicable. This is how you connect conversations",
    )
    convo_title: Optional[str] = Field(
        None,
        description="The title of the conversation, if applicable. This is needed if you change convo titles",
    )

class ChatSagemakerJson(BaseModel):
    """
    Customized class for sagemaker based generative ai endpoint. Modify as needed for which ever llm model you use.
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

class ChatBedrockJson(BaseModel):
    """
    Customized class for bedrock based generative ai endpoint. Modify as needed for which ever llm model you use.
    Additional Documentation here: https://docs.aws.amazon.com/bedrock/latest/userguide/api-setup.html
    """

    modelId: str = Field(
        ...,
        description="(Required if AWS Bedrock) The name of the model you want to use. ModelIds listed here: https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html.",
        example="ai21.j2-mid-v1",
    )
    prompt: str = Field(
        ...,
        description = "Single prompt to pass to the LLM model",
        example = "What is the difference between Python and Go?"
    )
    maxTokens: Optional[int] = Field(
        description = "The maximum number of tokens to generate per result. Optional, default = 16. (Source https://docs.ai21.com/reference/j2-complete-ref).",
        example=200
    )
    root_id: Optional[str] = Field(
        None,
        description="The root UUID of the conversation, if applicable. This is how you connect conversations",
    )
    convo_title: Optional[str] = Field(
        None,
        description="The title of the conversation, if applicable. This is needed if you change convo titles",
    )
    class Config:
        """
        Config to allow open inputs
        """

        extra = "allow"

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
