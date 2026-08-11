from pathlib import Path

import pytest

from py_structure_tools.cli import main, normalize_formats


def test_normalize_formats_all() -> None:
    assert normalize_formats(["all"]) == ("txt", "json", "yaml", "xml", "html")


def test_normalize_formats_removes_duplicates() -> None:
    assert normalize_formats(["txt", "txt", "html"]) == ("txt", "html")


def test_normalize_formats_rejects_invalid_format() -> None:
    with pytest.raises(ValueError):
        _ = normalize_formats(["pdf"])


def test_main_tree_prints_structure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    readme = tmp_path / "README.md"
    _ = readme.write_text("hello", encoding="utf-8")

    exit_code = main(["tree", "--root", str(tmp_path)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert tmp_path.name in captured.out
    assert "README.md" in captured.out


def test_main_export_writes_txt_file(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    _ = readme.write_text("hello", encoding="utf-8")

    output_dir = tmp_path / "exports"

    exit_code = main(
        [
            "export",
            "--root",
            str(tmp_path),
            "--output-dir",
            str(output_dir),
            "--basename",
            "structure",
            "--formats",
            "txt",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "structure.txt").is_file()


def test_main_export_all_formats(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    _ = readme.write_text("hello", encoding="utf-8")

    output_dir = tmp_path / "exports"

    exit_code = main(
        [
            "export",
            "--root",
            str(tmp_path),
            "--output-dir",
            str(output_dir),
            "--formats",
            "all",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "structure_repo.txt").is_file()
    assert (output_dir / "structure_repo.json").is_file()
    assert (output_dir / "structure_repo.yaml").is_file()
    assert (output_dir / "structure_repo.xml").is_file()
    assert (output_dir / "structure_repo.html").is_file()


def test_main_raises_for_missing_root(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(SystemExit):
        _ = main(["tree", "--root", str(missing)])
