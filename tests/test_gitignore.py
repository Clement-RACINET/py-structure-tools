from pathlib import Path

from py_structure_tools.gitignore import (
    GitIgnoreSpec,
    parse_gitignore_patterns,
    pattern_to_regex,
)


def test_parse_gitignore_patterns_returns_empty_when_missing(tmp_path: Path) -> None:
    assert parse_gitignore_patterns(tmp_path) == []


def test_parse_gitignore_patterns_ignores_comments_and_blank_lines(
    tmp_path: Path,
) -> None:
    gitignore = tmp_path / ".gitignore"
    _ = gitignore.write_text(
        """
# Comment

*.log
  # Indented comment
build/
""".strip(),
        encoding="utf-8",
    )

    assert parse_gitignore_patterns(tmp_path) == ["*.log", "build/"]


def test_pattern_to_regex_matches_simple_file() -> None:
    regex = pattern_to_regex("*.pyc")

    assert regex.search("module.pyc")
    assert regex.search("src/module.pyc")
    assert not regex.search("module.py")


def test_pattern_to_regex_matches_directory_prefix() -> None:
    regex = pattern_to_regex("__pycache__/")

    assert regex.search("__pycache__/")
    assert regex.search("src/__pycache__/file.pyc")
    assert not regex.search("src/cache/file.pyc")


def test_pattern_to_regex_ignores_negation_patterns() -> None:
    regex = pattern_to_regex("!important.log")

    assert not regex.search("important.log")
    assert not regex.search("src/important.log")


def test_pattern_to_regex_matches_anchored_pattern_only_at_root() -> None:
    regex = pattern_to_regex("/build")

    assert regex.search("build")
    assert regex.search("build/file.txt")
    assert not regex.search("src/build")
    assert not regex.search("src/build/file.txt")


def test_pattern_to_regex_matches_double_star_pattern() -> None:
    regex = pattern_to_regex("src/**/generated/*.py")

    assert regex.search("src/pkg/generated/model.py")
    assert regex.search("src/pkg/subpkg/generated/model.py")
    assert not regex.search("tests/pkg/generated/model.py")


def test_pattern_to_regex_matches_question_mark_pattern() -> None:
    regex = pattern_to_regex("file?.txt")

    assert regex.search("file1.txt")
    assert regex.search("src/fileA.txt")
    assert not regex.search("file12.txt")


def test_gitignore_spec_reads_patterns(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    _ = gitignore.write_text("*.log\nbuild/\n", encoding="utf-8")

    spec = GitIgnoreSpec(tmp_path)

    assert spec.match_file("debug.log")
    assert spec.match_file("build/")
    assert not spec.match_file("README.md")


def test_gitignore_spec_matches_directory_content(tmp_path: Path) -> None:
    gitignore = tmp_path / ".gitignore"
    _ = gitignore.write_text("dist/\n", encoding="utf-8")

    spec = GitIgnoreSpec(tmp_path)

    assert spec.match_file("dist/")
    assert spec.match_file("dist/app.js")
    assert spec.match_file("src/dist/app.js")


def test_empty_gitignore_spec_matches_nothing() -> None:
    spec = GitIgnoreSpec.empty()

    assert not spec.match_file("debug.log")
