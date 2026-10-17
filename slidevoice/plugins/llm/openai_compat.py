"""Small Chat Completions JSON adapter; no SDK or persisted credentials."""

from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from slidevoice.core.config import reject_secrets
from slidevoice.core.errors import InputInvalid, PluginUnavailable, StageFailed
from slidevoice.core.interfaces import LLMProvider
from slidevoice.core.registry import register


@register("llm", "openai_compat")
class OpenAICompat(LLMProvider):
    name = "openai_compat"
    version = "0.1.0"

    def healthcheck(self) -> None:
        reject_secrets(self.config)
        parsed = urlparse(str(self.config.get("base_url", "https://api.openai.com/v1")))
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or (
                parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            )
        ):
            raise InputInvalid("Use an HTTPS LLM endpoint (HTTP is allowed only on loopback).")
        if not os.environ.get(str(self.config.get("api_key_env", "LLM_API_KEY"))):
            raise PluginUnavailable(
                "LLM credential environment variable is not set.",
                remedy="Set llm.api_key_env in the process environment; never put keys in YAML.",
            )
        model = str(self.config.get("model", "")).strip()
        if not model or "<" in model:
            raise InputInvalid("Configure llm.model with your provider's model identifier.")
        if self.config.get("response_format", "json_schema") not in {"json_schema", "json_object"}:
            raise InputInvalid("llm.response_format must be json_schema or json_object.")

    def complete_json(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
        self.healthcheck()
        key = os.environ[str(self.config.get("api_key_env", "LLM_API_KEY"))]
        mode = self.config.get("response_format", "json_schema")
        payload: dict[str, Any] = {
            "model": self.config["model"],
            "temperature": float(self.config.get("temperature", 0.3)),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": mode},
        }
        if mode == "json_schema":
            payload["response_format"]["json_schema"] = {
                "name": "lecture_plan",
                "strict": True,
                "schema": schema,
            }
        else:
            payload["messages"][0]["content"] += "\nReturn JSON matching: " + json.dumps(schema)
        attempts = max(0, min(5, int(self.config.get("max_retries", 2)))) + 1
        endpoint = str(self.config.get("base_url", "https://api.openai.com/v1")).rstrip("/")
        with httpx.Client(
            timeout=float(self.config.get("timeout_sec", 60)), follow_redirects=False
        ) as client:
            for attempt in range(attempts):
                try:
                    response = client.post(
                        endpoint + "/chat/completions",
                        headers={"Authorization": f"Bearer {key}"},
                        json=payload,
                    )
                    if (
                        response.status_code == 429 or response.status_code >= 500
                    ) and attempt < attempts - 1:
                        time.sleep(min(2**attempt, 8))
                        continue
                    if response.status_code != 200:
                        raise StageFailed(
                            f"LLM request rejected (HTTP {response.status_code}).",
                            remedy="Check model, endpoint, quota and response_format support. No response body was logged.",
                        )
                    data = response.json()
                    choice = data["choices"][0]
                    if choice.get("finish_reason") not in {None, "stop"}:
                        raise ValueError("Incomplete generation")
                    content = choice["message"]["content"]
                    if not isinstance(content, str) or key in content:
                        raise ValueError("Invalid response")
                    result = json.loads(content)
                    if not isinstance(result, dict):
                        raise ValueError("Expected object")
                    reject_secrets(result)
                    return result
                except httpx.TransportError:
                    if attempt < attempts - 1:
                        time.sleep(min(2**attempt, 8))
                        continue
                    raise StageFailed("LLM transport failed after bounded retries.") from None
                except (ValueError, KeyError, IndexError, TypeError, AttributeError):
                    raise StageFailed(
                        "LLM returned invalid, incomplete or unsafe JSON.",
                        remedy="Use a model supporting structured JSON output and retry the script stage.",
                    ) from None
        raise StageFailed("LLM request failed.")
