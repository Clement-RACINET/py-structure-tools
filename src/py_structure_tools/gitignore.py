"""Minimal .gitignore support using only the Python standard library."""

from __future__ import annotations

import re
from pathlib import Path


def parse_gitignore_patterns(root: Path) -> list[str]:
    """Read raw patterns from .gitignore."""
    gitignore_path = root / ".gitignore"

    if not gitignore_path.exists():
        return []

    lines = gitignore_path.read_text(encoding="utf-8").splitlines()

    return [
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    ]


def pattern_to_regex(pattern: str) -> re.Pattern[str]:
    """Convert a minimal gitignore pattern to a compiled regex."""
    pattern = pattern.rstrip(" ")

    if pattern.startswith("!"):
        return re.compile(r"a^")

    dir_only = pattern.endswith("/")
    if dir_only:
        pattern = pattern[:-1]

    anchored = pattern.startswith("/")
    if anchored:
        pattern = pattern[1:]

    regex = ""
    index = 0

    while index < len(pattern):
        if pattern[index : index + 2] == "**":
            regex += ".*"
            index += 2

            if index < len(pattern) and pattern[index] == "/":
                index += 1

        elif pattern[index] == "*":
            regex += "[^/]*"
            index += 1

        elif pattern[index] == "?":
            regex += "[^/]"
            index += 1

        else:
            regex += re.escape(pattern[index])
            index += 1

    regex = f"^{regex}" if anchored else f"(^|/){regex}"

    if dir_only:
        regex += "(/|$)"
    else:
        regex += "(/.*)?$"

    return re.compile(regex)


class GitIgnoreSpec:
    """Minimal gitignore matcher."""

    def __init__(self, root: Path) -> None:
        """Initialize the matcher from root .gitignore patterns."""
        patterns = parse_gitignore_patterns(root)
        self._regexes: tuple[re.Pattern[str], ...] = tuple(
            pattern_to_regex(pattern) for pattern in patterns
        )

    @classmethod
    def empty(cls) -> GitIgnoreSpec:
        """Return an empty gitignore spec."""
        spec = cls.__new__(cls)
        spec._regexes = ()
        return spec

    def match_file(self, rel_path: str) -> bool:
        """Return whether a relative path matches any gitignore pattern."""
        return any(regex.search(rel_path) for regex in self._regexes)
