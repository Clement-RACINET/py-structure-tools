"""Formatting and statistics helpers shared by all renderers."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from py_structure_tools.model import TreeNode

_SIZE_UNITS: tuple[str, ...] = ("B", "KB", "MB", "GB", "TB")
_SIZE_BASE = 1024
_NO_EXTENSION = "(none)"


@dataclass(frozen=True, slots=True)
class TreeSummary:
    """Aggregated statistics about a tree (the root itself is not counted)."""

    directories: int
    files: int
    total_size: int | None
    errors: int
    extensions: tuple[tuple[str, int], ...]


def format_size(size: int) -> str:
    """Format a size in bytes as a human-readable string (e.g. ``1.5 KB``)."""
    value = float(size)

    for unit in _SIZE_UNITS[:-1]:
        if value < _SIZE_BASE:
            return f"{int(value)} B" if unit == "B" else f"{value:.1f} {unit}"
        value /= _SIZE_BASE

    return f"{value:.1f} {_SIZE_UNITS[-1]}"


def format_node_meta(node: TreeNode) -> str:
    """Return the metadata suffix of a node, or an empty string.

    Examples: `` (1.5 KB, modified 2026-10-21)`` or `` [ERROR: Permission denied]``.
    Dates are displayed in UTC.
    """
    parts: list[str] = []

    if node.size is not None:
        parts.append(format_size(node.size))

    if node.modified is not None:
        parts.append(f"modified {node.modified:%Y-%m-%d}")

    if node.created is not None:
        parts.append(f"created {node.created:%Y-%m-%d}")

    suffix = f" ({', '.join(parts)})" if parts else ""

    if node.error is not None:
        suffix += f" [ERROR: {node.error}]"

    return suffix


def compute_summary(root: TreeNode) -> TreeSummary:
    """Compute counts, total size and extension distribution for a tree."""
    directories = 0
    files = 0
    errors = 1 if root.error is not None else 0
    total_size = 0
    has_size = False
    extensions: Counter[str] = Counter()

    stack = list(root.children)

    while stack:
        node = stack.pop()

        if node.error is not None:
            errors += 1

        if node.is_dir:
            directories += 1
            stack.extend(node.children)
            continue

        files += 1
        extensions[PurePosixPath(node.name).suffix.lower() or _NO_EXTENSION] += 1

        if node.size is not None:
            has_size = True
            total_size += node.size

    return TreeSummary(
        directories=directories,
        files=files,
        total_size=total_size if has_size else None,
        errors=errors,
        extensions=tuple(sorted(extensions.items())),
    )


def format_summary_lines(summary: TreeSummary) -> list[str]:
    """Render a summary as plain-text lines."""
    lines = [f"{summary.directories} directories, {summary.files} files"]

    if summary.total_size is not None:
        lines.append(f"Total size: {format_size(summary.total_size)}")

    if summary.errors:
        lines.append(f"Errors: {summary.errors}")

    if summary.extensions:
        lines.append("By extension:")
        lines.extend(f"  {ext}: {count}" for ext, count in summary.extensions)

    return lines
