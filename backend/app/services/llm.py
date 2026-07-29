# backend/app/services/llm.py
import os
import time
from typing import TypeVar

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from app.config import get_settings

_llm_instances: dict[str, ChatGoogleGenerativeAI] = {}
StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


def _response_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
    return str(content)


def _configured_api_keys() -> list[str]:
    settings = get_settings()
    keys = [*settings.gemini_api_keys]
    primary_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not keys and primary_key:
        keys.append(primary_key)

    # Preserve priority while removing empty and duplicate keys.
    return list(dict.fromkeys(key for key in keys if key))


def get_llm(
    api_key: str | None = None,
) -> ChatGoogleGenerativeAI:
    settings = get_settings()
    api_key = api_key or next(iter(_configured_api_keys()), "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not configured.")

    if api_key not in _llm_instances:
        _llm_instances[api_key] = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=api_key,
            max_retries=2,
            timeout=120,
        )
    return _llm_instances[api_key]


def ask_llm(prompt: str, retries: int = 3, delay: float = 2.0) -> str:
    api_keys = _configured_api_keys()
    if not api_keys:
        raise RuntimeError("GEMINI_API_KEY not configured.")

    attempts = max(retries, len(api_keys))
    for attempt in range(attempts):
        api_key = api_keys[attempt % len(api_keys)]
        try:
            resp = get_llm(api_key=api_key).invoke(prompt)
            text = _response_text(resp.content)
            if not text:
                raise RuntimeError("LLM returned an empty response.")
            return text
        except Exception:
            if attempt < attempts - 1:
                time.sleep(delay * (attempt + 1))

    # Do not include provider errors because some responses echo credentials.
    raise RuntimeError(
        f"LLM API failed after trying {len(api_keys)} configured key(s)."
    ) from None


def ask_llm_structured(
    prompt: str,
    schema: type[StructuredOutput],
    retries: int = 3,
    delay: float = 2.0,
) -> StructuredOutput:
    """Invoke Gemini with a validated Pydantic response schema and key rotation."""
    api_keys = _configured_api_keys()
    if not api_keys:
        raise RuntimeError("GEMINI_API_KEY not configured.")

    attempts = max(retries, len(api_keys))
    for attempt in range(attempts):
        api_key = api_keys[attempt % len(api_keys)]
        try:
            structured_llm = get_llm(api_key=api_key).with_structured_output(schema)
            response = structured_llm.invoke(prompt)
            return response if isinstance(response, schema) else schema.model_validate(response)
        except Exception:
            if attempt < attempts - 1:
                time.sleep(delay * (attempt + 1))

    raise RuntimeError(
        f"Structured LLM API failed after trying {len(api_keys)} configured key(s)."
    ) from None
