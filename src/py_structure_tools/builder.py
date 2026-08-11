"""Repository tree builder."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path

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


def build_tree_node(
    path: Path,
    options: BuildOptions,
    current_depth: int = 0,
) -> TreeNode:
    """Build a structured tree representation from a filesystem path."""
    if path.is_file():
        return TreeNode(name=path.name, type="file")

    if options.max_depth is not None and current_depth >= options.max_depth:
        return TreeNode(name=path.name, type="directory")

    children = tuple(
        build_tree_node(
            child,
            options,
            current_depth=current_depth + 1,
        )
        for child in get_visible_entries(path, options)
    )

    return TreeNode(name=path.name, type="directory", children=children)
