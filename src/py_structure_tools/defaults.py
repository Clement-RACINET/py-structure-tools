"""Default settings for py-structure-tools."""

from __future__ import annotations

from py_structure_tools.model import ExportFormat

DEFAULT_OUTPUT_BASENAME = "structure_repo"

DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".pixi",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".tox",
        "node_modules",
        "__pypackages__",
    }
)

DEFAULT_EXCLUDE_FILES: tuple[str, ...] = (
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    "coverage.xml",
)

DEFAULT_FORMATS: tuple[ExportFormat, ...] = ("txt",)
