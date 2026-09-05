import os
import time
import random
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

import openai
from openai import OpenAI, APIStatusError, APITimeoutError, APIConnectionError

load_dotenv()

logger = logging.getLogger("flyrank.llm")


def get_llm_config() -> Dict[str, Any]:
    """Reads LLM configuration parameters from environment variables."""
    base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "openrouter/free")
    timeout = float(os.getenv("LLM_TIMEOUT", "30.0"))
    stub_mode = os.getenv("LLM_STUB", "0").lower() in ("1", "true", "yes")
    enabled = os.getenv("LLM_ENABLED", "true").lower() in ("1", "true", "yes")
    return {
        "base_url": base_url,
        "api_key": api_key,
        "model": model,
        "timeout": timeout,
        "stub_mode": stub_mode,
        "enabled": enabled,
    }


def get_openai_client() -> OpenAI:
    """
    Initializes an OpenAI-compatible client with explicit timeout and zero SDK-level retries.
    Custom retry logic with exponential backoff and jitter is handled in execute_chat_completion.
    """
    config = get_llm_config()
    return OpenAI(
        base_url=config["base_url"],
        api_key=config["api_key"] or "missing-key",
        timeout=config["timeout"],
        max_retries=0,  # We manage retries explicitly to prevent silent quota bleed
    )


class LLMTimeoutException(Exception):
    """Raised when an LLM request exceeds configured timeout."""
    pass


class LLMDisabledException(Exception):
    """Raised when LLM_ENABLED is false (kill switch activated)."""
    pass


class LLMClientException(Exception):
    """Raised on non-retryable 4xx client errors (e.g. 401, 403, 400)."""
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def execute_chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.1,
    max_retries: int = 3,
) -> tuple[str, Dict[str, Any]]:
    """
    Executes a chat completion call with explicit retry policy and error isolation.
    
    Retry Policy:
      - Retries on: 429 (rate limits), 5xx (server errors), and timeouts/network drops.
      - Uses exponential backoff (1s, 2s, 4s) with random jitter (+0.1 to +0.5s).
      - Respects Retry-After header if provided on 429.
      - Fails FAST on client errors: 400, 401, 403 (never retried).
      
    Returns:
      (raw_content, metadata_dict)
    """
    config = get_llm_config()
    if not config["enabled"]:
        raise LLMDisabledException("LLM integration disabled via LLM_ENABLED=false kill switch")

    target_model = model or config["model"]
    client = get_openai_client()

    attempt = 0
    start_time = time.perf_counter()

    while True:
        attempt += 1
        try:
            response = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            content = response.choices[0].message.content or ""
            usage = response.usage

            metadata = {
                "model": target_model,
                "input_tokens": usage.prompt_tokens if usage else None,
                "output_tokens": usage.completion_tokens if usage else None,
                "duration_ms": duration_ms,
                "attempts": attempt,
            }
            return content, metadata

        except APITimeoutError as e:
            if attempt > max_retries:
                raise LLMTimeoutException(f"LLM request timed out after {attempt} attempts: {e}")
            sleep_time = (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
            logger.warning(f"Timeout on attempt {attempt}/{max_retries}. Retrying in {sleep_time:.2f}s...")
            time.sleep(sleep_time)

        except APIConnectionError as e:
            if attempt > max_retries:
                raise LLMTimeoutException(f"LLM connection error after {attempt} attempts: {e}")
            sleep_time = (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
            logger.warning(f"Connection error on attempt {attempt}/{max_retries}. Retrying in {sleep_time:.2f}s...")
            time.sleep(sleep_time)

        except APIStatusError as e:
            status_code = e.status_code

            # Fail fast on client errors (400, 401, 403) — NEVER RETRY
            if status_code in (400, 401, 403):
                logger.error(f"Non-retryable client error {status_code} received from provider: {e.message}")
                raise LLMClientException(status_code=status_code, message=f"LLM provider returned {status_code}: {e.message}")

            # Check for Retry-After header on 429
            retry_after = None
            if hasattr(e, "response") and e.response is not None:
                retry_header = e.response.headers.get("retry-after")
                if retry_header:
                    try:
                        retry_after = float(retry_header)
                    except ValueError:
                        pass

            if attempt > max_retries:
                raise RuntimeError(f"LLM provider returned {status_code} after {attempt} attempts: {e.message}")

            if retry_after is not None:
                sleep_time = retry_after + random.uniform(0.1, 0.5)
                logger.warning(f"Received 429 with Retry-After: {retry_after}s. Sleeping {sleep_time:.2f}s...")
            else:
                sleep_time = (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
                logger.warning(f"Received HTTP {status_code} on attempt {attempt}/{max_retries}. Retrying in {sleep_time:.2f}s...")

            time.sleep(sleep_time)
