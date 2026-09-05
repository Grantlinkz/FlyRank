import os
import json
import re
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from pydantic import ValidationError

from src.llm.schema import (
    TaskCategory,
    TaskUrgency,
    TaskEffort,
    TaskTriageRequest,
    TaskTriageResponse,
    LLMCallTelemetry,
)
from src.llm.client import (
    get_llm_config,
    execute_chat_completion,
    LLMDisabledException,
    LLMTimeoutException,
    LLMClientException,
)

logger = logging.getLogger("flyrank.llm")

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
QUARANTINE_FILE = LOGS_DIR / "quarantine.jsonl"


class LLMQuarantineException(Exception):
    """Raised when model output fails validation after repair retry and is quarantined."""
    def __init__(self, message: str, details: Dict[str, Any]):
        super().__init__(message)
        self.details = details


def load_prompt(version: str = "task-triage-v1") -> str:
    """Loads prompt template from prompts/ directory."""
    prompt_path = PROMPTS_DIR / f"{version}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt specification file not found at: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def clean_json_output(raw_text: str) -> str:
    """
    Strips Markdown code fences (e.g. ```json ... ```) and extracts the outermost JSON object.
    """
    text = raw_text.strip()
    # Remove markdown code fences
    fence_pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
    match = re.match(fence_pattern, text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    
    # Extract first JSON object boundaries if wrapped in conversational filler
    if not (text.startswith("{") and text.endswith("}")):
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx + 1].strip()
            
    return text


def write_quarantine_log(entry: Dict[str, Any]) -> None:
    """Appends an unrepairable failure record to logs/quarantine.jsonl."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(QUARANTINE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def triage_task(
    request: TaskTriageRequest,
    stub: Optional[bool] = None,
    prompt_version: str = "task-triage-v1",
) -> Tuple[TaskTriageResponse, LLMCallTelemetry]:
    """
    Triages incoming task details with schema validation, repair retries, and quarantine handling.
    """
    config = get_llm_config()
    is_stub = config["stub_mode"] if stub is None else stub

    # Stage 1: Zero-cost Stub Mode
    if is_stub:
        response = TaskTriageResponse(
            category=TaskCategory.BUG,
            urgency=TaskUrgency.HIGH,
            estimated_effort=TaskEffort.MEDIUM_TASK,
            confidence=0.95,
            reason="[STUB] Connection pool exhaustion directly degrades system stability."
        )
        telemetry = LLMCallTelemetry(
            prompt_version=f"{prompt_version}-stub",
            model="stub-fixture",
            input_tokens=0,
            output_tokens=0,
            duration_ms=0.0,
            repaired=False,
        )
        # Structured log to stdout
        sys.stdout.write(json.dumps({"telemetry": telemetry.model_dump()}) + "\n")
        sys.stdout.flush()
        return response, telemetry

    # Operational Kill Switch check
    if not config["enabled"]:
        raise LLMDisabledException("LLM triage disabled via LLM_ENABLED=false kill switch")

    system_prompt = load_prompt(prompt_version)

    # Security Invariant: Keep user input strictly inside user role, JSON-encoded
    user_payload = {"title": request.title, "context": request.context}
    user_message_content = json.dumps(user_payload)

    initial_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message_content},
    ]

    raw_output, metadata = execute_chat_completion(initial_messages)
    cleaned_output = clean_json_output(raw_output)
    repaired = False
    validation_error_str = None

    try:
        validated_response = TaskTriageResponse.model_validate_json(cleaned_output)
    except (ValidationError, ValueError, json.JSONDecodeError) as err:
        validation_error_str = str(err)
        logger.warning(f"Initial validation failed: {validation_error_str}. Initiating single repair retry...")

        # Stage 3: Repair Retry — Exactly once
        repair_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message_content},
            {"role": "assistant", "content": raw_output},
            {
                "role": "user",
                "content": (
                    f"Your previous answer was rejected for this reason:\n{validation_error_str}\n\n"
                    "Return only corrected JSON matching the schema."
                )
            }
        ]

        repair_raw_output, repair_metadata = execute_chat_completion(repair_messages)
        repaired = True
        cleaned_repair_output = clean_json_output(repair_raw_output)

        # Update telemetry metrics to reflect total token consumption & duration
        metadata["input_tokens"] = (metadata["input_tokens"] or 0) + (repair_metadata.get("input_tokens") or 0)
        metadata["output_tokens"] = (metadata["output_tokens"] or 0) + (repair_metadata.get("output_tokens") or 0)
        metadata["duration_ms"] = round(metadata["duration_ms"] + repair_metadata.get("duration_ms", 0.0), 2)

        try:
            validated_response = TaskTriageResponse.model_validate_json(cleaned_repair_output)
        except (ValidationError, ValueError, json.JSONDecodeError) as final_err:
            # Stage 3 Quarantine: Persistent failure logged to logs/quarantine.jsonl
            quarantine_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt_version": prompt_version,
                "input": user_payload,
                "initial_raw_output": raw_output,
                "repair_raw_output": repair_raw_output,
                "error": str(final_err),
                "model": metadata.get("model"),
            }
            write_quarantine_log(quarantine_record)
            raise LLMQuarantineException(
                message="Model response failed schema validation after repair attempt and was quarantined.",
                details=quarantine_record
            )

    telemetry = LLMCallTelemetry(
        prompt_version=prompt_version,
        model=metadata.get("model", config["model"]),
        input_tokens=metadata.get("input_tokens", 0),
        output_tokens=metadata.get("output_tokens", 0),
        duration_ms=metadata.get("duration_ms", 0.0),
        repaired=repaired,
    )

    # Output structured single-line JSON log to stdout per call
    sys.stdout.write(json.dumps({"telemetry": telemetry.model_dump()}) + "\n")
    sys.stdout.flush()

    return validated_response, telemetry
