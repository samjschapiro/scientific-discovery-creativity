"""Single-turn model calls for sci_twist.

Kept deliberately small and this-track-local (no cross-track imports, per repo_usage.md).
Two providers behind one `complete()` signature: Claude via the native Anthropic SDK,
everything else via OpenRouter. Fails loudly — an empty response or a refusal is a crash,
never a silently recorded blank.
"""

import os

from dotenv import load_dotenv

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_TIMEOUT_S = 600.0


def _require_env(name: str) -> str:
    load_dotenv()
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"FATAL: {name} is not set. Copy .env.example to .env and fill it in.")
    return value


def complete(*, prompt: str, provider: str, model: str, max_tokens: int,
             thinking: str = "adaptive", effort: str = "high") -> dict:
    if provider == "anthropic":
        return _anthropic(prompt=prompt, model=model, max_tokens=max_tokens,
                          thinking=thinking, effort=effort)
    if provider == "openrouter":
        return _openrouter(prompt=prompt, model=model, max_tokens=max_tokens,
                          thinking=thinking, effort=effort)
    raise ValueError(f"FATAL: unknown provider '{provider}' (anthropic | openrouter)")


def _anthropic(*, prompt, model, max_tokens, thinking, effort) -> dict:
    import anthropic

    _require_env("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        thinking={"type": thinking},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError(f"FATAL: model refused. stop_details={resp.stop_details}")
    text = "\n".join(b.text for b in resp.content if b.type == "text")
    if not text.strip():
        raise RuntimeError(f"FATAL: empty response. stop_reason={resp.stop_reason}")
    return {
        "text": text,
        "reasoning": None,
        "model_returned": resp.model,
        "generation_id": resp.id,
        "cost_usd": None,  # Anthropic does not return a per-call price; not faked from a rate card.
        "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
    }


def _openrouter(*, prompt, model, max_tokens, thinking, effort) -> dict:
    import httpx

    key = _require_env("OPENROUTER_API_KEY")
    reasoning = {"enabled": False} if thinking == "disabled" else {"effort": effort}
    with httpx.Client(timeout=OPENROUTER_TIMEOUT_S,
                      headers={"Authorization": f"Bearer {key}"}) as client:
        resp = client.post(OPENROUTER_URL, json={
            "model": model,
            "max_tokens": max_tokens,
            "reasoning": reasoning,
            "usage": {"include": True},
            "messages": [{"role": "user", "content": prompt}],
        })
    resp.raise_for_status()
    body = resp.json()
    if "error" in body:
        raise RuntimeError(f"FATAL: OpenRouter error: {body['error']}")
    choice = body["choices"][0]
    text = choice["message"].get("content") or ""
    if not text.strip():
        raise RuntimeError(f"FATAL: empty response from {model}; finish={choice.get('finish_reason')}")
    usage = body.get("usage", {})
    if "cost" not in usage:
        raise RuntimeError(f"FATAL: OpenRouter returned no cost for {model}; refusing to run untracked.")
    return {
        "text": text,
        "reasoning": choice["message"].get("reasoning"),
        "model_returned": body.get("model"),
        "generation_id": body.get("id"),
        "cost_usd": usage["cost"],
        "usage": {"input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens")},
    }
