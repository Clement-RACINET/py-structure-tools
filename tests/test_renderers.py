import json
import xml.etree.ElementTree as ET
from pathlib import Path

from py_structure_tools.model import TreeNode
from py_structure_tools.renderers.html import build_html_document, count_nodes
from py_structure_tools.renderers.json import render_json_document
from py_structure_tools.renderers.txt import render_txt_document
from py_structure_tools.renderers.xml import export_xml
from py_structure_tools.renderers.yaml import render_yaml_document


def sample_tree() -> TreeNode:
    return TreeNode(
        name="repo",
        type="directory",
        children=(
            TreeNode(
                name="src",
                type="directory",
                children=(TreeNode(name="main.py", type="file"),),
            ),
            TreeNode(name="README.md", type="file"),
        ),
    )


def test_render_txt_document() -> None:
    content = render_txt_document(sample_tree())

    assert "repo" in content
    assert "├── src" in content
    assert "└── README.md" in content


def test_render_json_document() -> None:
    content = render_json_document(sample_tree())
    data = json.loads(content)

    assert data["name"] == "repo"
    assert data["children"][0]["name"] == "src"


def test_render_yaml_document() -> None:
    content = render_yaml_document(sample_tree())

    assert 'name: "repo"' in content
    assert 'type: "directory"' in content


def test_export_xml(tmp_path: Path) -> None:
    output = tmp_path / "structure.xml"

    export_xml(sample_tree(), output)

    tree = ET.parse(output)
    root = tree.getroot()

    assert root.tag == "directory"
    assert root.attrib["name"] == "repo"


def test_count_nodes() -> None:
    directories, files = count_nodes(sample_tree())

    assert directories == 2
    assert files == 2


def test_build_html_document() -> None:
    content = build_html_document(sample_tree())

    assert "<!doctype html>" in content
    assert "Repository structure: repo" in content
    assert "README.md" in content
