from __future__ import annotations

import re


_PARTICIPANT_PATTERNS = (
    re.compile(r"^participants?\s*\(\s*(\d{1,5})\s*\)$", re.IGNORECASE),
    re.compile(r"^participants?\s*:\s*(\d{1,5})$", re.IGNORECASE),
    re.compile(r"^participants?\s+(\d{1,5})$", re.IGNORECASE),
    re.compile(r"^(\d{1,5})\s+participants?$", re.IGNORECASE),
    re.compile(r"^\(\s*(\d{1,5})\s*\)\s*participants?$", re.IGNORECASE),
    re.compile(r"^attendees?\s*\(\s*(\d{1,5})\s*\)$", re.IGNORECASE),
    re.compile(r"^people\s*\(\s*(\d{1,5})\s*\)$", re.IGNORECASE),
)


def parse_participant_count(label: object) -> int | None:
    text = re.sub(r"\s+", " ", str(label or "")).strip()
    for pattern in _PARTICIPANT_PATTERNS:
        match = pattern.fullmatch(text)
        if match is not None:
            count = int(match.group(1))
            if count <= 10000:
                return count
    return None
