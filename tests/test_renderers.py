import json
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

from py_structure_tools.model import TreeNode
from py_structure_tools.renderers.html import build_html_document, count_nodes
from py_structure_tools.renderers.json import render_json_document
from py_structure_tools.renderers.txt import render_txt_document
from py_structure_tools.renderers.xml import export_xml, tree_node_to_xml_element
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


def make_meta_tree() -> TreeNode:
    """Build a small tree where every metadata field is set."""
    moment = datetime(2026, 10, 21, tzinfo=UTC)
    return TreeNode(
        name="root",
        type="directory",
        children=(
            TreeNode(
                name="a.py",
                type="file",
                size=2048,
                modified=moment,
                created=moment,
                error="Permission denied",
            ),
        ),
    )


def test_txt_renders_metadata_and_summary() -> None:
    document = render_txt_document(make_meta_tree(), show_summary=True)

    assert "a.py (2.0 KB, modified 2026-10-21, created 2026-10-21)" in document
    assert "[ERROR: Permission denied]" in document
    assert "Total size: 2.0 KB" in document


def test_yaml_renders_metadata_keys() -> None:
    document = render_yaml_document(make_meta_tree())

    assert "size: 2048" in document
    assert 'modified: "2026-10-21T00:00:00+00:00"' in document
    assert 'error: "Permission denied"' in document


def test_xml_renders_metadata_attributes() -> None:
    element = tree_node_to_xml_element(make_meta_tree())
    child = element[0]

    assert child.attrib["size"] == "2048"
    assert child.attrib["error"] == "Permission denied"
    assert child.attrib["modified"].startswith("2026-10-21")
