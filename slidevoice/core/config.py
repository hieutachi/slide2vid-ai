"""YAML defaults, recursive merge, and safety-critical validation."""

from __future__ import annotations

import math
from copy import deepcopy
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field, StrictBool, ValidationError

from .errors import InputInvalid
from .inputs import InputLimits

STAGES = ("render", "script", "normalize", "voice", "tts", "align", "subtitle", "avatar", "compose")


class ProjectConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    language: str = "vi"
    title: str = ""
    author: str = ""
    voice_consent: StrictBool = False


class TimingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    lead_in: float = Field(default=0.5, ge=0, allow_inf_nan=False)
    gap: float = Field(default=0.25, ge=0, allow_inf_nan=False)
    tail: float = Field(default=0.8, ge=0, allow_inf_nan=False)
    empty_slide_duration: float = Field(default=3, gt=0, allow_inf_nan=False)
    transition: float = Field(default=0.3, ge=0, allow_inf_nan=False)


class QAConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_cer: float = Field(default=0.15, ge=0, le=1)
    max_retries: int = Field(default=2, ge=0, le=10)
    target_lufs: float = Field(default=-16, ge=-70, le=-5)


def merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def reject_secrets(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in {"api_key", "token", "password", "secret", "authorization"}:
                raise InputInvalid(
                    "Literal credentials are forbidden; use an environment variable name."
                )
            if str(key).endswith("url") and isinstance(item, str) and ("@" in item or "?" in item):
                raise InputInvalid("Endpoint URLs must not contain credentials or query strings.")
            reject_secrets(item)
    elif isinstance(value, list):
        for item in value:
            reject_secrets(item)


def validate(config: dict[str, Any]) -> dict[str, Any]:
    reject_secrets(config)
    try:
        config["project"] = ProjectConfig.model_validate(config["project"]).model_dump()
        config["timing"] = TimingConfig.model_validate(config["timing"]).model_dump()
        config["qa"] = QAConfig.model_validate(config["qa"]).model_dump()
        config["limits"] = InputLimits.model_validate(config.get("limits", {})).model_dump()
        for stage in (*STAGES, "llm"):
            if not isinstance(config[stage], dict) or not isinstance(
                config[stage].get("plugin"), str
            ):
                raise ValueError("Each stage requires a plugin name")
        if (
            config["compose"]["plugin"] == "presenter"
            and config["script"]["plugin"] != "lecture_script"
        ):
            raise ValueError("presenter requires lecture_script")
        if config["voice"]["plugin"] == "preset_voice" and config["tts"]["plugin"] not in {
            "vieneu",
            "fake_tts",
        }:
            raise ValueError("preset_voice cannot be used as a personal cloning reference")
        for key in ("width", "height"):
            size = config["render"][key]
            if type(size) is not int or not 2 <= size <= 8192 or size % 2:
                raise ValueError("Dimensions must be positive even integers")
        speed = float(config["tts"]["speed"])
        fps = config["compose"]["fps"]
        if not math.isfinite(speed) or speed <= 0 or type(fps) is not int or not 1 <= fps <= 120:
            raise ValueError("Speed and fps must be positive")
        for value in config.values():
            if isinstance(value, dict) and any(
                isinstance(v, float) and not math.isfinite(v) for v in value.values()
            ):
                raise ValueError("Non-finite configuration values are forbidden")
    except (ValidationError, KeyError, TypeError, ValueError):
        raise InputInvalid(
            "Invalid configuration; check plugin names, consent and numeric ranges."
        ) from None
    return config


def load_config(path: Path | None = None) -> dict[str, Any]:
    defaults = yaml.safe_load(
        files("slidevoice.configs").joinpath("default.yaml").read_text(encoding="utf-8")
    )
    try:
        override = yaml.safe_load(path.read_text(encoding="utf-8")) if path else {}
        if override is None:
            override = {}
        if not isinstance(override, dict):
            raise ValueError("YAML must be a mapping")
        return validate(merge(defaults, override))
    except (OSError, yaml.YAMLError, ValueError):
        raise InputInvalid(
            "Cannot load YAML configuration; check the file and its syntax."
        ) from None
