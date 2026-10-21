"""Command-line interface for py-structure-tools."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import cast

from py_structure_tools.builder import BuildOptions, build_tree_node
from py_structure_tools.config import load_config
from py_structure_tools.defaults import DEFAULT_OUTPUT_BASENAME
from py_structure_tools.gitignore import GitIgnoreSpec
from py_structure_tools.local import (
    LOCAL_MODES,
    LocalMode,
    iter_targets,
    limit_depth,
    write_if_changed,
)
from py_structure_tools.model import SUPPORTED_FORMATS, ExportFormat, TreeNode
from py_structure_tools.printer import print_tree
from py_structure_tools.renderers.html import export_html
from py_structure_tools.renderers.json import export_json
from py_structure_tools.renderers.md import inject_block, render_embeddable_html
from py_structure_tools.renderers.txt import export_txt
from py_structure_tools.renderers.xml import export_xml
from py_structure_tools.renderers.yaml import export_yaml


@dataclass(frozen=True, slots=True)
class RuntimeOptions:
    """Resolved runtime options."""

    root: Path
    exclude_dirs: frozenset[str]
    exclude_files: tuple[str, ...]
    include_hidden: bool
    use_gitignore: bool
    max_depth: int | None


def normalize_formats(raw_formats: Sequence[str]) -> tuple[ExportFormat, ...]:
    """Normalize CLI format values."""
    lowered = [item.lower() for item in raw_formats]

    if "all" in lowered:
        return SUPPORTED_FORMATS

    invalid = [item for item in lowered if item not in SUPPORTED_FORMATS]

    if invalid:
        supported = ", ".join((*SUPPORTED_FORMATS, "all"))
        msg = (
            f"Unsupported format(s): {', '.join(invalid)}. "
            f"Supported values: {supported}."
        )
        raise ValueError(msg)

    seen: set[str] = set()
    formats: list[ExportFormat] = []

    for item in lowered:
        if item not in seen:
            seen.add(item)
            formats.append(cast(ExportFormat, item))

    return tuple(formats)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pystructure",
        description="Print and export repository structures.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    tree_parser = subparsers.add_parser("tree", help="Print repository tree.")
    add_common_options(tree_parser)

    export_parser = subparsers.add_parser("export", help="Export repository tree.")
    add_common_options(export_parser)
    export_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory where output files are written. Default: repository root.",
    )
    export_parser.add_argument(
        "--basename",
        type=str,
        default=None,
        help=f"Output basename. Default: {DEFAULT_OUTPUT_BASENAME}.",
    )
    export_parser.add_argument(
        "--formats",
        nargs="+",
        default=None,
        help="Formats to export: txt json yaml xml html all.",
    )
    export_parser.add_argument(
        "--open-depth",
        type=int,
        default=1,
        help="HTML only: directories open by default up to this depth.",
    )

    local_parser = subparsers.add_parser(
        "local",
        help="Write a structure file in the root and in each package or folder.",
    )
    add_common_options(local_parser)
    local_parser.add_argument(
        "--mode",
        choices=LOCAL_MODES,
        default="init",
        help=(
            "init: root + every directory containing __init__.py (default). "
            "all: root + every non-empty directory."
        ),
    )
    local_parser.add_argument(
        "--basename",
        type=str,
        default=None,
        help=f"Output basename. Default: {DEFAULT_OUTPUT_BASENAME}.",
    )
    local_parser.add_argument(
        "--formats",
        nargs="+",
        default=None,
        help="Formats to export: txt json yaml xml html all.",
    )
    local_parser.add_argument(
        "--open-depth",
        type=int,
        default=1,
        help="HTML only: directories open by default up to this depth.",
    )
    local_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created or updated without writing anything.",
    )
    local_parser.add_argument(
        "--check",
        action="store_true",
        help="Write nothing; exit with code 1 if any file is missing or outdated.",
    )
    readme_parser = subparsers.add_parser(
        "readme",
        help="Inject the repository tree into a README between markers.",
    )
    add_common_options(readme_parser)
    readme_parser.add_argument(
        "--file",
        type=Path,
        default=Path("README.md"),
        help="Markdown file to update. Default: README.md (relative to --root).",
    )
    readme_parser.add_argument(
        "--open-depth",
        type=int,
        default=1,
        help="Directories open by default up to this depth.",
    )
    readme_parser.add_argument(
        "--check",
        action="store_true",
        help="Write nothing; exit with code 1 if the README is outdated.",
    )

    return parser


def add_common_options(parser: argparse.ArgumentParser) -> None:
    """Add common tree-building options to a parser."""
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(),
        help="Root directory. Default: current directory.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help=(
            "Maximum tree depth. Default: unlimited or config value. "
            "With 'local', depth is relative to each generated file."
        ),
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories starting with '.'.",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Do not apply .gitignore patterns.",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to exclude. Can be passed multiple times.",
    )
    parser.add_argument(
        "--exclude-file",
        action="append",
        default=[],
        help="File glob pattern to exclude. Can be passed multiple times.",
    )


def resolve_runtime_options(namespace: argparse.Namespace) -> RuntimeOptions:
    """Resolve runtime options from defaults, config and CLI."""
    root = cast(Path, namespace.root).resolve()

    if not root.exists():
        raise SystemExit(f"Root directory does not exist: {root}")

    if not root.is_dir():
        raise SystemExit(f"Root path is not a directory: {root}")

    config = load_config(root)

    cli_exclude_dirs = frozenset(cast(list[str], namespace.exclude_dir))
    cli_exclude_files = tuple(cast(list[str], namespace.exclude_file))

    max_depth = (
        max(cast(int, namespace.max_depth), 0)
        if namespace.max_depth is not None
        else config.max_depth
    )

    return RuntimeOptions(
        root=root,
        exclude_dirs=frozenset(config.exclude_dirs | cli_exclude_dirs),
        exclude_files=(*config.exclude_files, *cli_exclude_files),
        include_hidden=bool(namespace.include_hidden) or config.include_hidden,
        use_gitignore=not bool(namespace.no_gitignore) and config.use_gitignore,
        max_depth=max_depth,
    )


def build_tree_from_options(options: RuntimeOptions) -> TreeNode:
    """Build a tree from resolved runtime options."""
    spec = (
        GitIgnoreSpec(options.root) if options.use_gitignore else GitIgnoreSpec.empty()
    )

    build_options = BuildOptions(
        spec=spec,
        root=options.root,
        exclude_dirs=options.exclude_dirs,
        exclude_files=options.exclude_files,
        include_hidden=options.include_hidden,
        max_depth=options.max_depth,
    )

    return build_tree_node(options.root, build_options)


def build_output_paths(
    output_dir: Path,
    basename: str,
) -> dict[ExportFormat, Path]:
    """Build output paths for all supported formats."""
    return {
        "txt": output_dir / f"{basename}.txt",
        "json": output_dir / f"{basename}.json",
        "yaml": output_dir / f"{basename}.yaml",
        "xml": output_dir / f"{basename}.xml",
        "html": output_dir / f"{basename}.html",
    }


def build_exporters(
    open_depth: int,
) -> dict[ExportFormat, Callable[[TreeNode, Path], None]]:
    """Build the exporter registry for all supported formats."""
    return {
        "txt": export_txt,
        "json": export_json,
        "yaml": export_yaml,
        "xml": export_xml,
        "html": lambda node, path: export_html(
            node,
            path,
            open_until_depth=open_depth,
        ),
    }


def run_tree(namespace: argparse.Namespace) -> int:
    """Run the tree command."""
    options = resolve_runtime_options(namespace)
    root_node = build_tree_from_options(options)

    print_tree(root_node)
    return 0


def run_export(namespace: argparse.Namespace) -> int:
    """Run the export command."""
    options = resolve_runtime_options(namespace)
    config = load_config(options.root)
    root_node = build_tree_from_options(options)

    raw_formats: Sequence[str] = (
        cast(list[str], namespace.formats)
        if namespace.formats is not None
        else config.default_formats
    )

    try:
        formats = normalize_formats(raw_formats)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    output_dir = (
        cast(Path, namespace.output_dir).resolve()
        if namespace.output_dir is not None
        else options.root
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    basename = (
        cast(str, namespace.basename)
        if namespace.basename is not None
        else config.output_basename
    )

    output_paths = build_output_paths(output_dir, basename)
    open_depth = max(cast(int, namespace.open_depth), 0)
    exporters = build_exporters(open_depth)

    for export_format in formats:
        output_path = output_paths[export_format]

        if output_path.exists():
            output_path.unlink()

        exporters[export_format](root_node, output_path)
        print(f"{export_format.upper()} structure exported to: {output_path}")

    return 0


def run_local(namespace: argparse.Namespace) -> int:
    """Run the local command.

    Build the full tree once, then write one structure file per target directory.
    """
    options = resolve_runtime_options(namespace)
    config = load_config(options.root)

    raw_formats: Sequence[str] = (
        cast(list[str], namespace.formats)
        if namespace.formats is not None
        else config.default_formats
    )

    try:
        formats = normalize_formats(raw_formats)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    basename = (
        cast(str, namespace.basename)
        if namespace.basename is not None
        else config.output_basename
    )

    mode = cast(LocalMode, namespace.mode)
    check = bool(namespace.check)
    apply = not (bool(namespace.dry_run) or check)
    open_depth = max(cast(int, namespace.open_depth), 0)

    # Depth is applied per generated file, so the global tree must be complete.
    local_depth = options.max_depth

    # Generated files must never appear in the structures they describe.
    generated_names = tuple(
        path.name for path in build_output_paths(Path(), basename).values()
    )
    full_options = replace(
        options,
        exclude_files=(*options.exclude_files, *generated_names),
        max_depth=None,
    )
    root_node = build_tree_from_options(full_options)

    exporters = build_exporters(open_depth)
    pending = 0

    for relative_dir, node in iter_targets(root_node, mode):
        subtree = limit_depth(node, local_depth)
        directory = options.root / relative_dir
        output_paths = build_output_paths(directory, basename)

        for export_format in formats:
            destination = output_paths[export_format]
            status = write_if_changed(
                exporters[export_format],
                subtree,
                destination,
                apply=apply,
            )

            if status == "unchanged":
                continue

            pending += 1
            label = status if apply else f"would be {status}"
            print(f"[{label}] {destination.relative_to(options.root).as_posix()}")

    if pending == 0:
        print("All local structures are up to date.")
    elif not apply:
        print(f"{pending} file(s) to create or update.")

    return 1 if (check and pending) else 0


def run_readme(namespace: argparse.Namespace) -> int:
    """Run the readme command: refresh the tree block inside a Markdown file."""
    options = resolve_runtime_options(namespace)

    readme_path = cast(Path, namespace.file)
    if not readme_path.is_absolute():
        readme_path = options.root / readme_path

    if not readme_path.is_file():
        raise SystemExit(f"File not found: {readme_path}")

    root_node = build_tree_from_options(options)
    open_depth = max(cast(int, namespace.open_depth), 0)
    block = render_embeddable_html(root_node, open_until_depth=open_depth)

    current = readme_path.read_text(encoding="utf-8")

    try:
        updated = inject_block(current, block)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if updated == current:
        print(f"{readme_path.name} is up to date.")
        return 0

    if bool(namespace.check):
        print(f"{readme_path.name} is outdated.")
        return 1

    readme_path.write_text(updated, encoding="utf-8")
    print(f"Structure injected into: {readme_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run pystructure."""
    parser = build_parser()
    namespace = parser.parse_args(argv)

    if namespace.command == "tree":
        return run_tree(namespace)

    if namespace.command == "export":
        return run_export(namespace)

    if namespace.command == "local":
        return run_local(namespace)

    if namespace.command == "readme":
        return run_readme(namespace)

    parser.error(f"Unknown command: {namespace.command}")
    return 2


def entrypoint(argv: list[str] | None = None) -> None:
    """Console-script entrypoint."""
    raise SystemExit(main(argv))


if __name__ == "__main__":
    entrypoint()
