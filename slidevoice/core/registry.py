"""Registry plugin (SPEC.md mục 4.3).

Ba đường đăng ký plugin (ưu tiên theo thứ tự):
1. `@register("tts", "xtts")` — plugin trong repo (mỗi file plugin tự khai báo).
2. Entry point group `slidevoice.plugins` — plugin cài ngoài qua pip (pyproject
   của plugin khai báo tên dạng `<kind>.<name>` trỏ tới lớp).
3. `registry.register_class(...)` — dùng trong test để cắm plugin giả.

Lõi chọn plugin bằng `create(kind, name, config, workdir)`; thêm plugin mới
không phải sửa lõi (nguyên tắc 3, mục 2).
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Callable
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, TypeVar

from .errors import PluginUnavailable
from .interfaces import Plugin

log = logging.getLogger("slidevoice.registry")

ENTRY_POINT_GROUP = "slidevoice.plugins"

# kind là tên interface (viết thường) -> lớp interface tương ứng.
_PLUGINS: dict[str, dict[str, type[Plugin]]] = {}
_EXTERNAL_LOADED = False

P = TypeVar("P", bound=type[Plugin])


def register(kind: str, name: str) -> Callable[[P], P]:
    """Decorator đăng ký một lớp plugin cho stage `kind` với tên `name`."""

    def deco(cls: P) -> P:
        register_class(kind, name, cls)
        return cls

    return deco


def register_class(kind: str, name: str, cls: type[Plugin]) -> None:
    kind = kind.lower()
    name = name.lower()
    bucket = _PLUGINS.setdefault(kind, {})
    if name in bucket:
        existing = bucket[name]
        if existing is not cls:
            log.warning(
                "Plugin %s.%s bị đăng ký đè: %s -> %s",
                kind,
                name,
                existing.__qualname__,
                cls.__qualname__,
            )
    bucket[name] = cls


def _load_entry_points() -> None:
    """Nạp plugin ngoài qua entry point `slidevoice.plugins` (chạy một lần)."""
    global _EXTERNAL_LOADED
    if _EXTERNAL_LOADED:
        return
    _EXTERNAL_LOADED = True
    eps = entry_points(group=ENTRY_POINT_GROUP)
    for ep in eps:
        try:
            kind, _, name = ep.name.partition(".")
            if not name:
                raise ValueError(f"tên entry point phải dạng '<kind>.<name>', nhận '{ep.name}'")
            cls = ep.load()
            if not (isinstance(cls, type) and issubclass(cls, Plugin)):
                raise TypeError(f"{ep.value} không phải lớp con của Plugin")
            register_class(kind, name, cls)
            log.info("Nạp plugin ngoài: %s.%s (%s)", kind, name, ep.value)
        except Exception:
            log.exception("Không nạp được entry point %s", ep.name)


def ensure_builtin_plugins_loaded() -> None:
    """Import các package plugin trong repo để decorator @register chạy."""
    for mod in (
        "slidevoice.plugins.render",
        "slidevoice.plugins.render.powerpoint",
        "slidevoice.plugins.render.libreoffice",
        "slidevoice.plugins.voice",
        "slidevoice.plugins.llm",
        "slidevoice.plugins.llm.openai_compat",
        "slidevoice.plugins.script",
        "slidevoice.plugins.script.lecture",
        "slidevoice.plugins.normalize",
        "slidevoice.plugins.tts",
        "slidevoice.plugins.align",
        "slidevoice.plugins.subtitle",
        "slidevoice.plugins.avatar",
        "slidevoice.plugins.compose",
        "slidevoice.plugins.compose.presenter",
    ):
        try:
            importlib.import_module(mod)
        except ImportError as exc:  # pragma: no cover - chỉ khi repo thiếu file
            log.debug("Bỏ qua package plugin %s: %s", mod, exc)


def available(kind: str) -> list[str]:
    """Danh sách tên plugin đã đăng ký cho `kind` (kể cả plugin ngoài)."""
    ensure_builtin_plugins_loaded()
    _load_entry_points()
    return sorted(_PLUGINS.get(kind.lower(), {}))


def get_class(kind: str, name: str) -> type[Plugin]:
    ensure_builtin_plugins_loaded()
    _load_entry_points()
    bucket = _PLUGINS.get(kind.lower(), {})
    cls = bucket.get(name.lower())
    if cls is None:
        raise PluginUnavailable(
            f"Không tìm thấy plugin '{name}' cho stage '{kind}'.",
            remedy=(
                f"Các plugin khả dụng: {', '.join(bucket) or '(không có)'}. "
                "Kiểm tra cấu hình `<stage>.plugin` hoặc cài thêm plugin có entry point "
                f"'{ENTRY_POINT_GROUP}'."
            ),
        )
    return cls


def create(kind: str, name: str, config: dict[str, Any], workdir: Path) -> Plugin:
    """Tạo thực thể plugin cho stage `kind`, healthcheck trước khi trả về."""
    cls = get_class(kind, name)
    plugin = cls(config, workdir)
    plugin.healthcheck()
    return plugin


def snapshot() -> dict[str, list[str]]:
    """Bản chụp registry (dùng cho `slidevoice plugins` và test)."""
    ensure_builtin_plugins_loaded()
    _load_entry_points()
    return {kind: available(kind) for kind in sorted(_PLUGINS)}
