"""Markdown-embeddable HTML renderer (for README files)."""

from __future__ import annotations

from html import escape

from py_structure_tools.model import TreeNode

START_MARKER = "<!-- pystructure:start -->"
END_MARKER = "<!-- pystructure:end -->"


def _render_node(node: TreeNode, depth: int, open_depth: int) -> list[str]:
    """Render one node as <li> lines, without any blank line."""
    name = escape(node.name)

    if node.is_file:
        return [f"<li>📄 {name}</li>"]

    if not node.children:
        return [f"<li>📁 {name}</li>"]

    open_attr = " open" if depth <= open_depth else ""
    icon = "📂" if open_attr else "📁"
    lines = [
        "<li>",
        f"<details{open_attr}>",
        f"<summary>{icon} <b>{name}</b> <sub>{len(node.children)}</sub></summary>",
        "<ul>",
    ]

    for child in node.children:
        lines.extend(_render_node(child, depth + 1, open_depth))

    lines.extend(["</ul>", "</details>", "</li>"])
    return lines


def render_embeddable_html(node: TreeNode, open_until_depth: int = 1) -> str:
    """Return a collapsible HTML tree that GitLab and GitHub render in Markdown.

    No blank line is emitted, so Markdown renderers keep the whole fragment
    as a single HTML block.
    """
    lines = ["<ul>", *_render_node(node, 0, open_until_depth), "</ul>"]
    return "\n".join(lines) + "\n"


def inject_block(text: str, block: str) -> str:
    """Replace the content between the pystructure markers.

    Raises:
        ValueError: If the start or end marker is missing or misplaced.

    """
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)

    if start == -1 or end == -1 or end < start:
        msg = f"Markers not found. Add {START_MARKER} and {END_MARKER} to the file."
        raise ValueError(msg)

    head = text[: start + len(START_MARKER)]
    return f"{head}\n{block.rstrip()}\n{text[end:]}"
