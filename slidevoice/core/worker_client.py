"""Shared HTTP contract: JSON only, artifacts exchanged via mounted workdir."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import httpx

from .config import reject_secrets
from .errors import InputInvalid, PluginUnavailable, StageFailed


class WorkerClient:
    def __init__(
        self,
        base_url: str,
        workdir: Path,
        timeout: float = 60,
        retries: int = 2,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        reject_secrets({"worker_url": base_url})
        if timeout <= 0 or not 0 <= retries <= 10:
            raise InputInvalid("Worker timeout must be positive and retries between 0 and 10.")
        self.workdir = workdir.resolve()
        self.retries = retries
        self.client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            transport=transport,
            follow_redirects=False,
        )

    def __enter__(self) -> WorkerClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.client.close()

    def shared_path(self, path: Path) -> str:
        resolved = (self.workdir / path).resolve()
        if not resolved.is_relative_to(self.workdir):
            raise InputInvalid("Worker files must stay inside the shared job directory.")
        return resolved.relative_to(self.workdir).as_posix()

    def healthcheck(self) -> None:
        try:
            response = self.client.get("health")
            response.raise_for_status()
            data = response.json()
            if data.get("status") not in {"ok", "ready", "healthy"}:
                raise ValueError("unhealthy")
        except (httpx.HTTPError, ValueError, AttributeError):
            raise PluginUnavailable(
                "Worker is unavailable.",
                remedy="Start the worker and verify worker_url and shared volume.",
            ) from None

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        reject_secrets(payload)
        if any("base64" in str(k).lower() for k in payload):
            raise InputInvalid("Use shared relative file paths, not base64 payloads.")
        for attempt in range(self.retries + 1):
            try:
                response = self.client.post("run", json=payload)
                if (
                    response.status_code == 429 or response.status_code >= 500
                ) and attempt < self.retries:
                    time.sleep(min(2**attempt, 8))
                    continue
                response.raise_for_status()
                result = response.json()
                if not isinstance(result, dict):
                    raise ValueError("Expected JSON object")
                return result
            except httpx.TransportError:
                if attempt < self.retries:
                    time.sleep(min(2**attempt, 8))
                    continue
                raise PluginUnavailable(
                    "Worker connection failed.", remedy="Check worker health and timeout."
                ) from None
            except (httpx.HTTPStatusError, ValueError):
                raise StageFailed(
                    "Worker returned an invalid response; consult worker logs (secrets are not logged here)."
                ) from None
        raise StageFailed("Worker retry budget exhausted.")
