"""Terminal tree printing."""

from __future__ import annotations

from py_structure_tools.model import TreeNode
from py_structure_tools.renderers.txt import render_txt_document


def print_tree(root_node: TreeNode) -> None:
    """Print a tree to stdout."""
    print(render_txt_document(root_node), end="")
