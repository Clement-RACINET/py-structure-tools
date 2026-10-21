"""YAML renderer without third-party dependencies."""

from __future__ import annotations

from pathlib import Path

from py_structure_tools.model import TreeNode


def yaml_quote(value: str) -> str:
    """Quote a string for generated YAML."""
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )

    return f'"{escaped}"'


def render_yaml_node(
    node: TreeNode,
    indent: int = 0,
    as_list_item: bool = False,
) -> list[str]:
    """Render a tree node as YAML lines (metadata keys only when set)."""
    spaces = " " * indent
    prefix = "- " if as_list_item else ""

    lines = [f"{spaces}{prefix}name: {yaml_quote(node.name)}"]
    child_indent = indent + (2 if as_list_item else 0)
    pad = " " * child_indent

    lines.append(f"{pad}type: {yaml_quote(node.type)}")

    if node.size is not None:
        lines.append(f"{pad}size: {node.size}")

    if node.modified is not None:
        lines.append(f"{pad}modified: {yaml_quote(node.modified.isoformat())}")

    if node.created is not None:
        lines.append(f"{pad}created: {yaml_quote(node.created.isoformat())}")

    if node.error is not None:
        lines.append(f"{pad}error: {yaml_quote(node.error)}")

    if node.is_dir:
        lines.append(f"{pad}children:")

        if node.children:
            for child in node.children:
                lines.extend(
                    render_yaml_node(
                        child,
                        indent=child_indent + 2,
                        as_list_item=True,
                    )
                )
        else:
            lines.append(f"{' ' * (child_indent + 2)}[]")

    return lines


def render_yaml_document(root_node: TreeNode) -> str:
    """Render a complete YAML document."""
    return "\n".join(render_yaml_node(root_node)) + "\n"


def export_yaml(root_node: TreeNode, output_path: Path) -> None:
    """Export tree as YAML."""
    _ = output_path.write_text(render_yaml_document(root_node), encoding="utf-8")
