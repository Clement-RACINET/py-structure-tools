from pathlib import Path

from py_structure_tools.builder import BuildOptions, build_tree_node
from py_structure_tools.gitignore import GitIgnoreSpec


def make_build_options(
    root: Path,
    *,
    exclude_dirs: frozenset[str] = frozenset(),
    exclude_files: tuple[str, ...] = (),
    include_hidden: bool = True,
    max_depth: int | None = None,
) -> BuildOptions:
    return BuildOptions(
        spec=GitIgnoreSpec.empty(),
        root=root,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        include_hidden=include_hidden,
        max_depth=max_depth,
    )


def test_build_tree_node_sorts_directories_before_files(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    readme = tmp_path / "README.md"
    _ = readme.write_text("hello", encoding="utf-8")

    node = build_tree_node(tmp_path, make_build_options(tmp_path))

    assert [child.name for child in node.children] == ["src", "README.md"]


def test_build_tree_node_excludes_directories(tmp_path: Path) -> None:
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()

    node = build_tree_node(
        tmp_path,
        make_build_options(tmp_path, exclude_dirs=frozenset({"sandbox"})),
    )

    assert node.children == ()


def test_build_tree_node_excludes_files_by_pattern(tmp_path: Path) -> None:
    log = tmp_path / "debug.log"
    _ = log.write_text("log", encoding="utf-8")

    node = build_tree_node(
        tmp_path,
        make_build_options(tmp_path, exclude_files=("*.log",)),
    )

    assert node.children == ()


def test_build_tree_node_respects_max_depth(tmp_path: Path) -> None:
    nested = tmp_path / "src" / "pkg"
    nested.mkdir(parents=True)

    node = build_tree_node(
        tmp_path,
        make_build_options(tmp_path, max_depth=1),
    )

    assert len(node.children) == 1
    assert node.children[0].name == "src"
    assert node.children[0].children == ()
