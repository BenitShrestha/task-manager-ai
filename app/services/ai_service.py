import json
import time

from google import genai
from pydantic import ValidationError

from app.config import settings
from app.schemas.ai import GeneratedTaskList

client = genai.Client(api_key=settings.gemini_api_key)

SYSTEM_PROMPT = """You extract discrete tasks from a person's free-text description of their day or week.

Return ONLY valid JSON matching this exact schema, with no prose, no markdown fences:
{
  "tasks": [
    {
      "title": "string",
      "description": "string or null",
      "priority": "low" | "medium" | "high",
      "deadline": "ISO 8601 datetime string or null"
    }
  ]
}

Infer priority or deadline only when reasonably implied by the text. If no tasks are found, return {"tasks": []}.
"""


class AIGenerationError(Exception):
    pass


def _call_model(text: str, strict_reminder: bool = False) -> str:
    prompt = SYSTEM_PROMPT
    if strict_reminder:
        prompt += "\nIMPORTANT: Return ONLY the JSON object. No other text."

    last_error: Exception | None = None
    for attempt in range(2):  # 1 try + 1 retry on timeout/5xx
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{prompt}\n\nUser input:\n{text}",
                config={"response_mime_type": "application/json"},
            )
            return response.text
        except Exception as e:
            last_error = e
            time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s
    raise AIGenerationError(f"LLM call failed after retries: {last_error}")


def generate_tasks_from_text(text: str) -> GeneratedTaskList:
    raw = _call_model(text)

    try:
        parsed = json.loads(raw)
        return GeneratedTaskList.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError):
        # one retry with a stricter reminder
        raw = _call_model(text, strict_reminder=True)
        try:
            parsed = json.loads(raw)
            return GeneratedTaskList.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            raise AIGenerationError(f"Model returned invalid JSON: {e}")