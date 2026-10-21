"""Tests for local structure generation."""

from __future__ import annotations

from pathlib import Path

from py_structure_tools.cli import main
from py_structure_tools.local import iter_targets, limit_depth
from py_structure_tools.model import TreeNode


def make_project(root: Path) -> None:
    (root / "pkg" / "sub").mkdir(parents=True)
    (root / "pkg" / "plain").mkdir()
    (root / "pkg" / "__init__.py").touch()
    (root / "pkg" / "mod.py").touch()
    (root / "pkg" / "sub" / "__init__.py").touch()
    (root / "pkg" / "plain" / "data.txt").touch()


def sample_tree() -> TreeNode:
    return TreeNode(
        name="root",
        type="directory",
        children=(
            TreeNode(
                name="pkg",
                type="directory",
                children=(
                    TreeNode(name="__init__.py", type="file"),
                    TreeNode(
                        name="deep",
                        type="directory",
                        children=(TreeNode(name="a.py", type="file"),),
                    ),
                ),
            ),
            TreeNode(name="README.md", type="file"),
        ),
    )


def test_iter_targets_init_mode() -> None:
    targets = [path.as_posix() for path, _ in iter_targets(sample_tree(), "init")]

    assert targets == [".", "pkg"]


def test_iter_targets_all_mode() -> None:
    targets = [path.as_posix() for path, _ in iter_targets(sample_tree(), "all")]

    assert targets == [".", "pkg", "pkg/deep"]


def test_limit_depth_is_relative_to_node() -> None:
    pkg = sample_tree().children[0]

    limited = limit_depth(pkg, 1)

    assert [child.name for child in limited.children] == ["__init__.py", "deep"]
    assert limited.children[1].children == ()


def test_local_init_creates_files_in_packages_and_root(tmp_path: Path) -> None:
    make_project(tmp_path)

    code = main(
        [
            "local",
            "--root",
            str(tmp_path),
            "--basename",
            "structure",
            "--formats",
            "txt",
            "json",
        ]
    )

    assert code == 0
    assert (tmp_path / "structure.txt").exists()
    assert (tmp_path / "structure.json").exists()
    assert (tmp_path / "pkg" / "structure.txt").exists()
    assert (tmp_path / "pkg" / "sub" / "structure.json").exists()
    assert not (tmp_path / "pkg" / "plain" / "structure.txt").exists()


def test_local_all_includes_plain_directories(tmp_path: Path) -> None:
    make_project(tmp_path)

    main(
        [
            "local",
            "--root",
            str(tmp_path),
            "--mode",
            "all",
            "--basename",
            "structure",
            "--formats",
            "txt",
        ]
    )

    assert (tmp_path / "pkg" / "plain" / "structure.txt").exists()


def test_generated_files_are_not_in_their_own_structure(tmp_path: Path) -> None:
    make_project(tmp_path)
    args = [
        "local",
        "--root",
        str(tmp_path),
        "--basename",
        "structure",
        "--formats",
        "txt",
    ]

    main(args)
    main(args)

    content = (tmp_path / "pkg" / "structure.txt").read_text(encoding="utf-8")

    assert "structure.txt" not in content


def test_check_and_dry_run(tmp_path: Path) -> None:
    make_project(tmp_path)
    base = [
        "local",
        "--root",
        str(tmp_path),
        "--basename",
        "structure",
        "--formats",
        "txt",
    ]

    assert main([*base, "--dry-run"]) == 0
    assert not (tmp_path / "structure.txt").exists()

    assert main([*base, "--check"]) == 1

    main(base)
    assert main([*base, "--check"]) == 0

    (tmp_path / "pkg" / "new_module.py").touch()
    assert main([*base, "--check"]) == 1
