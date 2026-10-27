"""
LLM Integration — OpenRouter client abstraction.

All LLM calls go through this module. Swapping providers
means changing only this file.
"""
import structlog
from openai import AsyncOpenAI

from app.config import settings

logger = structlog.get_logger(__name__)


def get_llm_client() -> AsyncOpenAI:
    """Return an AsyncOpenAI client pointed at OpenRouter."""
    return AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "https://metago.in",
            "X-Title": "Metago AI Marketing Platform",
        },
    )


async def llm_complete(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """
    Simple completion helper for single-turn LLM calls.

    Returns the response content string.
    Raises on API errors.
    """
    if not settings.OPENROUTER_API_KEY:
        # Demo mode: return a mock response
        logger.warning("llm_mock_response", reason="No API key configured")
        return f"[DEMO MODE] Mock LLM response for prompt: {prompt[:100]}..."

    client = get_llm_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    effective_model = model or settings.DEFAULT_LLM_MODEL
    logger.info("llm_request", model=effective_model, prompt_len=len(prompt))

    response = await client.chat.completions.create(
        model=effective_model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    content = response.choices[0].message.content or ""
    logger.info(
        "llm_response",
        model=effective_model,
        tokens_used=response.usage.total_tokens if response.usage else None,
        response_len=len(content),
    )
    return content
