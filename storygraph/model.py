from __future__ import annotations

import re
import unicodedata

NODE_TYPES = {
    "character",
    "location",
    "organization",
    "object",
    "event",
    "secret",
    "clue",
    "foreshadow",
    "chapter",
    "scene",
    "rule",
    "goal",
    "belief",
    "conflict",
    "relationship",
    "concept",
}

RELATION_TYPES = {
    "knows",
    "does_not_know",
    "knows_person",
    "trusts",
    "distrusts",
    "loves",
    "hates",
    "ally_of",
    "enemy_of",
    "parent_of",
    "sibling_of",
    "married_to",
    "owns",
    "gives_to",
    "receives_from",
    "located_at",
    "member_of",
    "wants",
    "fears",
    "believes",
    "causes",
    "witnesses",
    "learns",
    "reveals",
    "hides_from",
    "appears_in",
    "participates_in",
    "foreshadows",
    "pays_off",
    "contradicts",
    "occurs_before",
    "occurs_after",
    "related_to",
}

CONFIDENCE_LEVELS = {"EXTRACTED", "INFERRED", "AMBIGUOUS"}


def normalize_name(value: str) -> str:
    """Normalize a name for exact alias matching without fuzzy guessing."""
    text = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"[\s\-_·・.。]+", "", text)


def entity_terms(node: dict) -> set[str]:
    terms: set[str] = set()
    label = node.get("label")
    if isinstance(label, str) and label.strip():
        terms.add(normalize_name(label))
    aliases = node.get("aliases")
    if isinstance(aliases, list):
        for alias in aliases:
            if isinstance(alias, str) and alias.strip():
                terms.add(normalize_name(alias))
    return {term for term in terms if term}
