"""
This is the primary file where the FastAPI object is created. 
All LLM gateway endpoints in this repo are built off the FastAPI framework.
"""
import codecs
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy import DDL

import src.modules.auto_models
from src.modules.chat import chat_router
from src.modules.common import RequestException
from src.modules.logger import log_request

DESCRIPTION = "\
This API Gateway will proxy calls to public LLM APIs.\
"

try:
    # pylint: disable=unspecified-encoding
    with open("src/VERSION", "r") as version_file:
        VERSION = version_file.read().strip()
except FileNotFoundError:
    VERSION = "error"

tags_metadata = [
    {
        "name": "ChatGPT",
        "description": "Operations related to Chatting with chat-gpt.",
    },
]

app = FastAPI(
    title="LLM Gateway",
    description=DESCRIPTION,
    version=VERSION,
    openapi_tags=tags_metadata)

# Tighten up the origins list if you can
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    """
    Logging middleware for any request to the app
    """
    log_request(request)

    try:
        response = await call_next(request)
    except Exception as error:
        print(f"Error in call_next: {error}")
        raise
    return response


@app.get("/", include_in_schema=False)
def index():
    """
    redirecting index searches to docs page
    """
    return RedirectResponse(url="/docs")


@app.get("/ping", include_in_schema=False)
def ping():
    """
    sample return 200 to confirm api is in working state
    """
    return 200


app.include_router(chat_router)


def read(rel_path):
    """
    reads a file for the first line, used for getting version info
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as file_path:
        return file_path.read()


@app.exception_handler(RequestException)
async def request_exception_handler(request: Request, exc: RequestException):
    """
    request exception handler
    """
    # pylint: disable=unused-argument
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! {exc.msg}"},
    )
