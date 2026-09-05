import os
from openai import OpenAI

# AI version: No explicit timeout set (defaults to 10 minutes), no custom backoff or retry isolation
def get_client():
    return OpenAI(
        base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=os.getenv("LLM_API_KEY", "")
    )
