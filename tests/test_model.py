from py_structure_tools.model import TreeNode


def test_tree_node_properties() -> None:
    directory = TreeNode(name="src", type="directory")
    file = TreeNode(name="README.md", type="file")

    assert directory.is_dir
    assert not directory.is_file
    assert file.is_file
    assert not file.is_dir
