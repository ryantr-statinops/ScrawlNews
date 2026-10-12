import re
from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_tracked_documentation_contains_no_secret_values():
    tracked_docs = [
        ROOT / "README.md",
        ROOT / "SETUP.md",
        * (ROOT / "docs").rglob("*.md"),
        * (ROOT / "planning").rglob("*.md"),
    ]
    secret_patterns = (
        re.compile(r"sk-(?:or-)?[A-Za-z0-9_-]{20,}"),
        re.compile(r"\b\d{8,}:[A-Za-z0-9_-]{20,}\b"),
    )

    for path in tracked_docs:
        text = path.read_text(encoding="utf-8")
        assert not any(pattern.search(text) for pattern in secret_patterns), path
