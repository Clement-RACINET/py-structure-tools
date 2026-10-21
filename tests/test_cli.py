from pathlib import Path

import pytest

from py_structure_tools import __version__
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


def test_export_from_json_is_quiet_and_writes_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--from-json must render without scanning, and --quiet must print nothing."""
    source = tmp_path / "source.json"
    _ = source.write_text(
        '{"name": "root", "type": "directory", "children": '
        '[{"name": "a.py", "type": "file", "size": 42}]}',
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    code = main(
        [
            "export",
            "--root",
            str(tmp_path),
            "--from-json",
            str(source),
            "--output-dir",
            str(out_dir),
            "--basename",
            "result",
            "--formats",
            "txt",
            "--quiet",
        ]
    )

    assert code == 0
    assert capsys.readouterr().out == ""
    assert "a.py (42 B)" in (out_dir / "result.txt").read_text(encoding="utf-8")


def test_tree_with_size_and_summary(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--size and --summary must show sizes and the final statistics."""
    _ = (tmp_path / "a.txt").write_text("hello", encoding="utf-8")

    code = main(["tree", "--root", str(tmp_path), "--size", "--summary"])

    output = capsys.readouterr().out
    assert code == 0
    assert "a.txt (5 B)" in output
    assert "0 directories, 1 files" in output
    assert "Total size: 5 B" in output


def test_version_flag_prints_package_version(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])

    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"pystructure {__version__}"
