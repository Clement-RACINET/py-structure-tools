"""Core data model for repository structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

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
    """Repository tree node."""

    name: str
    type: NodeType
    children: tuple[TreeNode, ...] = field(default_factory=tuple)

    @property
    def is_dir(self) -> bool:
        """Return whether this node is a directory."""
        return self.type == "directory"

    @property
    def is_file(self) -> bool:
        """Return whether this node is a file."""
        return self.type == "file"
