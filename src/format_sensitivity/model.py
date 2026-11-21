"""Single-turn model calls, one class per provider.

Both providers expose the same `complete()` signature and return the same record
shape, so the orchestration script never branches on provider.

Claude is called through the native Anthropic SDK, not through OpenRouter, even
though OpenRouter would serve it. Routing one arm of an experiment through an
extra hop that silently normalizes reasoning parameters is not worth the
convenience. If you want a Claude arm, use `provider: anthropic`.
"""

import os

import anthropic
import httpx
from dotenv import load_dotenv

VALID_THINKING = ("adaptive", "disabled")

# Anthropic accepts five effort levels; OpenRouter's reasoning API accepts three.
VALID_EFFORT = {
    "anthropic": ("low", "medium", "high", "xhigh", "max"),
    "openrouter": ("low", "medium", "high"),
}

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_TIMEOUT_S = 600.0


def _require_env(name: str) -> str:
    load_dotenv()
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"FATAL: {name} is not set. Copy .env.example to .env and fill it in, "
            f"or export the variable."
        )
    return value


def _validate(provider: str, thinking: str, effort: str) -> None:
    if thinking not in VALID_THINKING:
        raise ValueError(f"FATAL: thinking must be one of {VALID_THINKING}, got '{thinking}'")

    allowed = VALID_EFFORT[provider]
    if effort not in allowed:
        raise ValueError(
            f"FATAL: provider '{provider}' accepts effort {allowed}, got '{effort}'"
        )


class AnthropicProvider:
    name = "anthropic"

    def __init__(self) -> None:
        _require_env("ANTHROPIC_API_KEY")
        self._client = anthropic.Anthropic()

    def complete(self, *, prompt, model, max_tokens, thinking, effort) -> dict:
        _validate(self.name, thinking, effort)

        response = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            thinking={"type": thinking},
            output_config={"effort": effort},
            messages=[{"role": "user", "content": prompt}],
        )

        if response.stop_reason == "refusal":
            raise RuntimeError(f"FATAL: model refused. stop_details={response.stop_details}")

        text = "\n".join(b.text for b in response.content if b.type == "text")
        if not text.strip():
            raise RuntimeError(f"FATAL: empty response. stop_reason={response.stop_reason}")

        return {
            "text": text,
            "reasoning": None,
            "finish_reason": response.stop_reason,
            "model_returned": response.model,
            "generation_id": response.id,
            # The Anthropic API does not return a per-call price. Left null rather
            # than derived from a hardcoded rate card that will silently go stale.
            "cost_usd": None,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }


class OpenRouterProvider:
    """Raw HTTP against OpenRouter's chat-completions endpoint.

    OpenRouter can return HTTP 200 with an `error` object in the body, and can
    return a null `content` alongside a populated `reasoning` field. Both are
    treated as failures rather than silently recorded as empty responses.
    """

    name = "openrouter"

    def __init__(self) -> None:
        key = _require_env("OPENROUTER_API_KEY")
        self._client = httpx.Client(
            timeout=OPENROUTER_TIMEOUT_S,
            headers={"Authorization": f"Bearer {key}"},
        )

    def complete(self, *, prompt, model, max_tokens, thinking, effort) -> dict:
        _validate(self.name, thinking, effort)

        reasoning = {"enabled": False} if thinking == "disabled" else {"effort": effort}

        response = self._client.post(
            OPENROUTER_URL,
            json={
                "model": model,
                "max_tokens": max_tokens,
                "reasoning": reasoning,
                # Opt in to per-call accounting; without this `usage.cost` is absent.
                "usage": {"include": True},
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        body = response.json()

        if "error" in body:
            raise RuntimeError(f"FATAL: OpenRouter returned an error: {body['error']}")

        choice = body["choices"][0]
        text = choice["message"].get("content") or ""
        if not text.strip():
            raise RuntimeError(
                f"FATAL: empty response from {model}. "
                f"finish_reason={choice.get('finish_reason')}"
            )

        usage = body.get("usage", {})
        if "cost" not in usage:
            raise RuntimeError(
                f"FATAL: OpenRouter returned no cost for {model}. "
                f"Cost accounting is required; refusing to run untracked."
            )

        return {
            "text": text,
            "reasoning": choice["message"].get("reasoning"),
            "finish_reason": choice.get("finish_reason"),
            "model_returned": body.get("model"),
            "generation_id": body.get("id"),
            "cost_usd": usage["cost"],
            "usage": {
                "input_tokens": usage.get("prompt_tokens"),
                "output_tokens": usage.get("completion_tokens"),
                "reasoning_tokens": usage.get("completion_tokens_details", {}).get(
                    "reasoning_tokens"
                ),
            },
        }


PROVIDERS = {"anthropic": AnthropicProvider, "openrouter": OpenRouterProvider}


def build_provider(name: str):
    if name not in PROVIDERS:
        raise ValueError(f"FATAL: unknown provider '{name}'. Known: {sorted(PROVIDERS)}")
    return PROVIDERS[name]()
