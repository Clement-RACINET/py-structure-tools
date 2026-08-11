from pathlib import Path

import pytest

from py_structure_tools.config import load_config


def test_load_config_without_pyproject_uses_defaults(tmp_path: Path) -> None:
    config = load_config(tmp_path)

    assert ".git" in config.exclude_dirs
    assert "*.pyc" in config.exclude_files
    assert config.use_gitignore


def test_load_config_without_tool_table_uses_defaults(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[project]
name = "demo"
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert ".git" in config.exclude_dirs
    assert config.default_formats == ("txt",)


def test_load_config_without_py_structure_tools_table_uses_defaults(
    tmp_path: Path,
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.ruff]
line-length = 88
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert ".git" in config.exclude_dirs
    assert config.default_formats == ("txt",)


def test_load_config_reads_project_options(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
exclude_dirs = ["sandbox", "litterature"]
exclude_files = ["*.log"]
include_hidden = true
use_gitignore = false
max_depth = 3
default_formats = ["txt", "html"]
output_basename = "repo_tree"
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert "sandbox" in config.exclude_dirs
    assert "litterature" in config.exclude_dirs
    assert "*.log" in config.exclude_files
    assert config.include_hidden
    assert not config.use_gitignore
    assert config.max_depth == 3
    assert config.default_formats == ("txt", "html")
    assert config.output_basename == "repo_tree"


def test_load_config_clamps_negative_max_depth_to_zero(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
max_depth = -3
""".strip(),
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert config.max_depth == 0


def test_load_config_rejects_invalid_exclude_dirs_type(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
exclude_dirs = "sandbox"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError):
        _ = load_config(tmp_path)


def test_load_config_rejects_invalid_exclude_dirs_item(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
exclude_dirs = ["sandbox", 42]
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError):
        _ = load_config(tmp_path)


def test_load_config_rejects_invalid_exclude_files_type(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
exclude_files = "*.log"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError):
        _ = load_config(tmp_path)


def test_load_config_rejects_invalid_include_hidden_type(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
include_hidden = "yes"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError):
        _ = load_config(tmp_path)


def test_load_config_rejects_invalid_use_gitignore_type(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
use_gitignore = "false"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError):
        _ = load_config(tmp_path)


def test_load_config_rejects_invalid_max_depth_type(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
max_depth = "3"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError):
        _ = load_config(tmp_path)


def test_load_config_rejects_invalid_output_basename_type(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
output_basename = 123
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError):
        _ = load_config(tmp_path)


def test_load_config_rejects_invalid_default_formats_type(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
default_formats = "txt"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(TypeError):
        _ = load_config(tmp_path)


def test_load_config_rejects_invalid_format(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[tool.py-structure-tools]
default_formats = ["txt", "pdf"]
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        _ = load_config(tmp_path)
