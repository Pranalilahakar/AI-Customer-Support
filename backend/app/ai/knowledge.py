import re
from pathlib import Path

KNOWLEDGE_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "knowledge_base"
)

WORD_PATTERN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(WORD_PATTERN.findall(text.lower()))


def search_knowledge(query: str, limit: int = 3) -> dict:
    """Return locally sourced passages ranked by query-word overlap."""
    query_tokens = _tokens(query)

    if not query_tokens:
        return {
            "query": query,
            "results": [],
            "message": "Enter a query containing searchable words.",
        }

    results = []

    if KNOWLEDGE_DIR.is_dir():
        for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
            content = path.read_text(encoding="utf-8-sig")
            sections = re.split(r"(?m)(?=^##\s+)", content)

            for section in sections:
                section = section.strip()
                if not section:
                    continue

                section_tokens = _tokens(section)
                overlap = query_tokens & section_tokens

                if not overlap:
                    continue

                score = len(overlap) / len(query_tokens)
                heading_match = re.search(r"(?m)^#{1,2}\s+(.+)$", section)
                heading = heading_match.group(1).strip() if heading_match else path.stem

                results.append({
                    "source": path.name,
                    "section": heading,
                    "passage": section[:1800],
                    "matched_terms": sorted(overlap),
                    "score": round(score, 4),
                })

    results.sort(
        key=lambda item: (-item["score"], item["source"], item["section"])
    )
    results = results[:max(1, min(limit, 5))]

    return {
        "query": query,
        "results": results,
        "message": (
            "Results are excerpts from local documents. "
            "Verify guidance against approved company policy before using it."
            if results
            else "No matching passage was found. Do not infer an answer from this knowledge base."
        ),
    }
