"""Configuration loading from pyproject.toml."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeAlias, cast

from py_structure_tools.defaults import (
    DEFAULT_EXCLUDE_DIRS,
    DEFAULT_EXCLUDE_FILES,
    DEFAULT_FORMATS,
    DEFAULT_OUTPUT_BASENAME,
)
from py_structure_tools.model import SUPPORTED_FORMATS, ExportFormat

TomlValue: TypeAlias = (
    str | int | float | bool | list["TomlValue"] | dict[str, "TomlValue"] | None
)


@dataclass(frozen=True, slots=True)
class StructureConfig:
    """Configuration for py-structure-tools."""

    exclude_dirs: frozenset[str] = field(default_factory=lambda: DEFAULT_EXCLUDE_DIRS)
    exclude_files: tuple[str, ...] = DEFAULT_EXCLUDE_FILES
    include_hidden: bool = False
    use_gitignore: bool = True
    max_depth: int | None = None
    default_formats: tuple[ExportFormat, ...] = DEFAULT_FORMATS
    output_basename: str = DEFAULT_OUTPUT_BASENAME


def _get_table(data: dict[str, TomlValue], key: str) -> dict[str, TomlValue] | None:
    """Return a nested TOML table when present."""
    value = data.get(key)

    if isinstance(value, dict):
        return value

    return None


def _get_string_list(data: dict[str, TomlValue], key: str) -> list[str]:
    """Return a string list from a TOML table."""
    value = data.get(key)

    if value is None:
        return []

    if not isinstance(value, list):
        msg = f"[tool.py-structure-tools].{key} must be a list of strings."
        raise TypeError(msg)

    strings: list[str] = []

    for item in value:
        if not isinstance(item, str):
            msg = f"[tool.py-structure-tools].{key} must contain only strings."
            raise TypeError(msg)
        strings.append(item)

    return strings


def _get_bool(
    data: dict[str, TomlValue],
    key: str,
    default: bool,
) -> bool:
    """Return a boolean config value."""
    value = data.get(key)

    if value is None:
        return default

    if not isinstance(value, bool):
        msg = f"[tool.py-structure-tools].{key} must be a boolean."
        raise TypeError(msg)

    return value


def _get_optional_int(data: dict[str, TomlValue], key: str) -> int | None:
    """Return an optional integer config value."""
    value = data.get(key)

    if value is None:
        return None

    if not isinstance(value, int):
        msg = f"[tool.py-structure-tools].{key} must be an integer."
        raise TypeError(msg)

    return max(value, 0)


def _get_string(
    data: dict[str, TomlValue],
    key: str,
    default: str,
) -> str:
    """Return a string config value."""
    value = data.get(key)

    if value is None:
        return default

    if not isinstance(value, str):
        msg = f"[tool.py-structure-tools].{key} must be a string."
        raise TypeError(msg)

    return value


def _parse_formats(raw_formats: list[str]) -> tuple[ExportFormat, ...]:
    """Validate configured export formats."""
    formats: list[ExportFormat] = []

    for item in raw_formats:
        lowered = item.lower()

        if lowered not in SUPPORTED_FORMATS:
            supported = ", ".join(SUPPORTED_FORMATS)
            msg = f"Unsupported format in config: {item}. Supported: {supported}."
            raise ValueError(msg)

        formats.append(lowered)

    return tuple(formats)


def load_config(root: Path) -> StructureConfig:
    """Load configuration from pyproject.toml."""
    pyproject_path = root / "pyproject.toml"

    if not pyproject_path.is_file():
        return StructureConfig()

    with pyproject_path.open("rb") as file:
        raw_data = tomllib.load(file)

    data = cast(dict[str, TomlValue], raw_data)

    tool_data = _get_table(data, "tool")
    if tool_data is None:
        return StructureConfig()

    config_data = _get_table(tool_data, "py-structure-tools")
    if config_data is None:
        return StructureConfig()

    configured_exclude_dirs = _get_string_list(config_data, "exclude_dirs")
    configured_exclude_files = _get_string_list(config_data, "exclude_files")
    configured_formats = _get_string_list(config_data, "default_formats")

    exclude_dirs = frozenset(DEFAULT_EXCLUDE_DIRS | frozenset(configured_exclude_dirs))
    exclude_files = (
        *DEFAULT_EXCLUDE_FILES,
        *configured_exclude_files,
    )

    return StructureConfig(
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        include_hidden=_get_bool(config_data, "include_hidden", False),
        use_gitignore=_get_bool(config_data, "use_gitignore", True),
        max_depth=_get_optional_int(config_data, "max_depth"),
        default_formats=(
            _parse_formats(configured_formats)
            if configured_formats
            else DEFAULT_FORMATS
        ),
        output_basename=_get_string(
            config_data,
            "output_basename",
            DEFAULT_OUTPUT_BASENAME,
        ),
    )
