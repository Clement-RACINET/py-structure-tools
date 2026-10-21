"""Tests for README tree injection."""

from __future__ import annotations

from pathlib import Path

import pytest

from py_structure_tools.cli import main
from py_structure_tools.model import TreeNode
from py_structure_tools.renderers.md import (
    END_MARKER,
    START_MARKER,
    inject_block,
    render_embeddable_html,
)


def sample_tree() -> TreeNode:
    return TreeNode(
        name="root",
        type="directory",
        children=(
            TreeNode(
                name="src",
                type="directory",
                children=(TreeNode(name="a<b>.py", type="file"),),
            ),
            TreeNode(name="README.md", type="file"),
        ),
    )


def test_render_has_no_blank_line_and_escapes_names() -> None:
    html = render_embeddable_html(sample_tree())

    assert "\n\n" not in html
    assert "a&lt;b&gt;.py" in html
    assert "<details open>" in html


def test_open_depth_zero_closes_children() -> None:
    html = render_embeddable_html(sample_tree(), open_until_depth=0)

    assert html.count("<details open>") == 1
    assert "<details>" in html


def test_inject_block_replaces_content_between_markers() -> None:
    text = f"intro\n{START_MARKER}\nold\n{END_MARKER}\noutro\n"

    result = inject_block(text, "new\n")

    assert result == f"intro\n{START_MARKER}\nnew\n{END_MARKER}\noutro\n"


def test_inject_block_requires_markers() -> None:
    with pytest.raises(ValueError, match="Markers not found"):
        inject_block("no markers", "x")


def test_readme_command_is_idempotent_and_checkable(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").touch()
    readme = tmp_path / "README.md"
    readme.write_text(f"# T\n{START_MARKER}\n{END_MARKER}\n", encoding="utf-8")
    base = ["readme", "--root", str(tmp_path)]

    assert main([*base, "--check"]) == 1
    assert main(base) == 0
    assert "mod.py" in readme.read_text(encoding="utf-8")
    assert main([*base, "--check"]) == 0
