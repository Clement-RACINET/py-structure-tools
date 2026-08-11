"""XML renderer."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from py_structure_tools.model import TreeNode


def tree_node_to_xml_element(node: TreeNode) -> ET.Element:
    """Convert a tree node to an XML element."""
    tag = "directory" if node.is_dir else "file"
    element = ET.Element(tag, {"name": node.name})

    if node.is_dir:
        for child in node.children:
            element.append(tree_node_to_xml_element(child))

    return element


def export_xml(root_node: TreeNode, output_path: Path) -> None:
    """Export tree as XML."""
    root_element = tree_node_to_xml_element(root_node)
    tree = ET.ElementTree(root_element)
    ET.indent(tree, space="  ", level=0)

    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True,
        short_empty_elements=True,
    )
