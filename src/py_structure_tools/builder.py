"""Repository tree builder."""

from __future__ import annotations

import fnmatch
import os
import sys
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from stat import S_ISREG
from typing import cast

from py_structure_tools.gitignore import GitIgnoreSpec
from py_structure_tools.model import TreeNode


@dataclass(frozen=True, slots=True)
class BuildOptions:
    """Options used to build a repository tree."""

    spec: GitIgnoreSpec
    root: Path
    exclude_dirs: frozenset[str]
    exclude_files: tuple[str, ...]
    include_hidden: bool
    max_depth: int | None
    collect_size: bool = False
    collect_dates: bool = False


@dataclass(frozen=True, slots=True)
class FileMetadata:
    """Metadata read from the filesystem for a single path."""

    size: int | None = None
    modified: datetime | None = None
    created: datetime | None = None
    error: str | None = None


def should_ignore(
    path: Path,
    options: BuildOptions,
) -> bool:
    """Return whether a path should be ignored."""
    if path.is_dir() and path.name in options.exclude_dirs:
        return True

    if path.is_file() and any(
        fnmatch.fnmatch(path.name, pattern) for pattern in options.exclude_files
    ):
        return True

    if not options.include_hidden and path.name.startswith("."):
        return True

    rel_path = path.relative_to(options.root).as_posix()

    if path.is_dir():
        rel_path += "/"

    return options.spec.match_file(rel_path)


def get_visible_entries(
    directory: Path,
    options: BuildOptions,
) -> tuple[Path, ...]:
    """Return visible children sorted with directories first."""
    entries = [path for path in directory.iterdir() if not should_ignore(path, options)]

    return tuple(sorted(entries, key=lambda path: (path.is_file(), path.name.lower())))


def _creation_timestamp(stat_result: os.stat_result) -> float | None:
    """Return the creation timestamp when the platform provides one.

    ``st_birthtime`` exists on macOS/BSD (and on Windows from Python 3.12).
    On older Windows, ``st_ctime`` is the creation time. On Linux, ``st_ctime``
    is the metadata change time, so no creation date is reported.
    """
    birth = cast("float | None", getattr(stat_result, "st_birthtime", None))

    if birth is not None:
        return birth

    if sys.platform == "win32":
        return stat_result.st_ctime

    return None


def read_metadata(path: Path, options: BuildOptions) -> FileMetadata:
    """Read the requested metadata, capturing OS errors instead of raising."""
    if not (options.collect_size or options.collect_dates):
        return FileMetadata()

    try:
        info = path.stat()
    except OSError as exc:
        return FileMetadata(error=exc.strerror or type(exc).__name__)

    created_timestamp = _creation_timestamp(info) if options.collect_dates else None

    return FileMetadata(
        size=info.st_size if options.collect_size and S_ISREG(info.st_mode) else None,
        modified=(
            datetime.fromtimestamp(info.st_mtime, tz=UTC)
            if options.collect_dates
            else None
        ),
        created=(
            datetime.fromtimestamp(created_timestamp, tz=UTC)
            if created_timestamp is not None
            else None
        ),
    )


def _with_metadata(node: TreeNode, metadata: FileMetadata) -> TreeNode:
    """Return a copy of a node enriched with the given metadata."""
    return replace(
        node,
        size=metadata.size,
        modified=metadata.modified,
        created=metadata.created,
        error=metadata.error,
    )


def build_tree_node(
    path: Path,
    options: BuildOptions,
    current_depth: int = 0,
) -> TreeNode:
    """Build a structured tree representation from a filesystem path."""
    metadata = read_metadata(path, options)

    if path.is_file():
        return _with_metadata(TreeNode(name=path.name, type="file"), metadata)

    if options.max_depth is not None and current_depth >= options.max_depth:
        return _with_metadata(TreeNode(name=path.name, type="directory"), metadata)

    try:
        entries = get_visible_entries(path, options)
    except OSError as exc:
        # Unreadable directory: keep it in the tree and flag the error.
        failed = replace(metadata, error=exc.strerror or type(exc).__name__)
        return _with_metadata(TreeNode(name=path.name, type="directory"), failed)

    children = tuple(
        build_tree_node(child, options, current_depth=current_depth + 1)
        for child in entries
    )

    return _with_metadata(
        TreeNode(name=path.name, type="directory", children=children),
        metadata,
    )
