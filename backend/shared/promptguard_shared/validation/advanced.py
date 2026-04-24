import math
import re
from typing import Iterable


_WORD_RE = re.compile(r"[a-zA-Z0-9]+")
_URL_RE = re.compile(r"https?://[^\s)]+", re.IGNORECASE)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text or "")]


def _cosine_similarity(a: dict[str, int], b: dict[str, int]) -> float:
    if not a or not b:
        return 0.0
    dot = 0.0
    for k, v in a.items():
        dot += v * b.get(k, 0)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_similarity(expected: str, actual: str) -> float:
    tokens_a = _tokenize(expected)
    tokens_b = _tokenize(actual)
    freq_a: dict[str, int] = {}
    freq_b: dict[str, int] = {}
    for t in tokens_a:
        freq_a[t] = freq_a.get(t, 0) + 1
    for t in tokens_b:
        freq_b[t] = freq_b.get(t, 0) + 1
    return _cosine_similarity(freq_a, freq_b)


def toxicity_hits(text: str, blocklist: Iterable[str]) -> list[str]:
    lowered = (text or "").lower()
    hits = []
    for term in blocklist:
        if term and term.lower() in lowered:
            hits.append(term)
    return hits


def hallucination_hits(text: str, allowed_sources: Iterable[str] | None) -> list[str]:
    if not allowed_sources:
        return []
    allowed = {s.lower() for s in allowed_sources if s}
    hits = []
    for url in _URL_RE.findall(text or ""):
        url_l = url.lower()
        if not any(url_l.startswith(s) for s in allowed):
            hits.append(url)
    return hits
