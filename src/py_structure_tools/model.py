"""Core data model for repository structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, TypeAlias

if TYPE_CHECKING:
    from datetime import datetime

NodeType: TypeAlias = Literal["directory", "file"]
ExportFormat: TypeAlias = Literal["txt", "json", "yaml", "xml", "html"]


SUPPORTED_FORMATS: tuple[ExportFormat, ...] = (
    "txt",
    "json",
    "yaml",
    "xml",
    "html",
)


@dataclass(frozen=True, slots=True)
class TreeNode:
    """Repository tree node.

    Metadata fields are optional: they stay ``None`` unless the builder was
    asked to collect them, so existing code keeps working unchanged.
    """

    name: str
    type: NodeType
    children: tuple[TreeNode, ...] = field(default_factory=tuple)
    size: int | None = None
    """File size in bytes (files only)."""
    modified: datetime | None = None
    """Last modification time (timezone-aware, UTC)."""
    created: datetime | None = None
    """Creation time (timezone-aware, UTC), when the platform exposes it."""
    error: str | None = None
    """Error message if the node could not be read (permissions, etc.)."""

    @property
    def is_dir(self) -> bool:
        """Return whether this node is a directory."""
        return self.type == "directory"

    @property
    def is_file(self) -> bool:
        """Return whether this node is a file."""
        return self.type == "file"
