from py_structure_tools.model import TreeNode
from py_structure_tools.stats import (
    compute_summary,
    format_node_meta,
    format_size,
    format_summary_lines,
)

EXPECTED_FILES = 3
EXPECTED_TOTAL_SIZE = 16


def make_tree() -> TreeNode:
    """Build a tree with two .py files, one extensionless file and one error."""
    return TreeNode(
        name="root",
        type="directory",
        children=(
            TreeNode(name="a.py", type="file", size=10),
            TreeNode(name="b.PY", type="file", size=5),
            TreeNode(
                name="sub",
                type="directory",
                error="Permission denied",
                children=(TreeNode(name="LICENSE", type="file", size=1),),
            ),
        ),
    )


def test_format_size_uses_adapted_unit() -> None:
    assert format_size(512) == "512 B"
    assert format_size(1536) == "1.5 KB"
    assert format_size(5 * 1024**2) == "5.0 MB"
    assert format_size(5 * 1024**4) == "5.0 TB"


def test_format_node_meta_is_empty_without_metadata() -> None:
    assert format_node_meta(TreeNode(name="x", type="file")) == ""


def test_format_node_meta_shows_size() -> None:
    assert format_node_meta(TreeNode(name="x", type="file", size=2048)) == " (2.0 KB)"


def test_format_node_meta_shows_error() -> None:
    node = TreeNode(name="x", type="directory", error="Permission denied")

    assert format_node_meta(node) == " [ERROR: Permission denied]"


def test_compute_summary_counts_nodes_and_extensions() -> None:
    summary = compute_summary(make_tree())

    assert summary.directories == 1
    assert summary.files == EXPECTED_FILES
    assert summary.total_size == EXPECTED_TOTAL_SIZE
    assert summary.errors == 1
    assert dict(summary.extensions) == {".py": 2, "(none)": 1}


def test_compute_summary_total_size_is_none_without_sizes() -> None:
    root = TreeNode(
        name="root",
        type="directory",
        children=(TreeNode(name="a.py", type="file"),),
    )

    assert compute_summary(root).total_size is None


def test_format_summary_lines_contains_all_sections() -> None:
    lines = format_summary_lines(compute_summary(make_tree()))

    assert lines[0] == "1 directories, 3 files"
    assert "Total size: 16 B" in lines
    assert "Errors: 1" in lines
    assert "  .py: 2" in lines
