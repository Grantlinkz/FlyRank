import json
from .client import get_client
from .schema import TaskTriageRequest, TaskTriageResponse

# AI version: Concatenates user input directly into system prompt (prompt injection risk!)
# Does not implement repair retry, zero-cost stub mode, telemetry logging, or quarantine logging
def triage_task(request: TaskTriageRequest) -> TaskTriageResponse:
    client = get_client()
    
    prompt = f"""
    You are an assistant that classifies tasks.
    Task title: {request.title}
    Task context: {request.context}
    
    Return JSON with category, urgency, estimated_effort, confidence, reason.
    """
    
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[{"role": "user", "content": prompt}],
    )
    
    content = response.choices[0].message.content
    data = json.loads(content)
    return TaskTriageResponse(**data)
