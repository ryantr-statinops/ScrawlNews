import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
DOCS = ROOT / "docs"
README = ROOT / "README.md"
CONTEXT = ROOT / "docs" / "PROJECT_KNOWLEDGE" / "AGENT_CONTEXT.md"


def _local_markdown_links(path: Path) -> list[Path]:
    links = re.findall(r"\[[^]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8"))
    return [ROOT / link for link in links if not link.startswith(("http://", "https://", "#"))]


def test_readme_context_links_exist():
    links = _local_markdown_links(README)

    assert CONTEXT in links
    assert all(path.exists() for path in links)


def test_context_has_required_sections_and_review_date():
    text = CONTEXT.read_text(encoding="utf-8")
    required = (
        "## Project purpose",
        "## Runtime topology",
        "## Backend and orchestration",
        "## Storage ownership",
        "## Client boundaries",
        "## Configuration and security",
        "## Testing and verification",
        "## Git and change workflow",
        "## Source-of-truth hierarchy",
        "## Known limitations",
        "## Required agent handoff",
    )

    assert all(section in text for section in required)
    assert re.search(r"Last reviewed: 20\d\d-\d\d-\d\d", text)
    assert len(text.split()) <= 4000


def test_context_runtime_contract_matches_compose():
    context = CONTEXT.read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "localhost:6767" in context
    assert "localhost:6768" in context
    assert '"6767:80"' in compose
    assert '"6768:3000"' in compose
    assert "Celery Beat is the production scheduler" in context
    assert "Dagster is shadow-only" in context


def test_context_and_docs_have_no_secret_values():
    tracked_docs = [README, CONTEXT, *DOCS.rglob("*.md")]
    secret_patterns = (
        re.compile(r"sk-(?:or-)?[A-Za-z0-9_-]{20,}"),
        re.compile(r"\b\d{8,}:[A-Za-z0-9_-]{20,}\b"),
    )

    for path in set(tracked_docs):
        text = path.read_text(encoding="utf-8")
        assert not any(pattern.search(text) for pattern in secret_patterns), path
