import os

OPEN_AI     = "OPEN_AI"
BEDROCK     = "BEDROCK"
SAGEMAKER   = "SAGEMAKER"
AWS_REGION      = os.environ["AWS_REGION"]
BEDROCK_ASSUMED_ROLE = os.environ["BEDROCK_ASSUMED_ROLE"]

CONTENT_TYPE    = os.environ["LLM_API_CONTENT_TYPE"]
ENABLE_SUBM_API = os.environ["ENABLE_SUBMISSIONS_API"]
LLM_TYPE        = os.environ["LLM_TYPE"]
MODEL_ID        = os.environ["MODEL_ID"] 
URL             = os.environ["LLM_ENDPOINT"]
URL_IMAGE       = os.environ["LLM_IMG_ENDPOINT"]
LLM_API_AUTH    = os.environ["LLM_API_AUTHORIZATION"]
