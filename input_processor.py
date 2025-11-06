"""
Phase 2 - Keyword Generation (Input Strategy)
Keyword Generation Module for Facebook Group Search

Purpose:
- Read team/sport data from Excel (.xlsx) or CSV files
- Generate search keywords based on patterns
- Normalize and deduplicate keywords

Input Sources:
- Excel files (.xlsx) via pandas/openpyxl
- CSV files
- Fallback to minimal static list if no files found

Keyword Patterns Generated:
For each team name found in input files:
- "{Team} Tickets" - e.g., "Arizona Cardinals Tickets"
- "{Team} Ticket Exchange" - e.g., "Atlanta Falcons Ticket Exchange"
- "{Team} Verified Tickets" - e.g., "Baltimore Ravens Verified Tickets"
- "{Team} Official Tickets" - e.g., "Buffalo Bills Official Tickets"

Workflow:
1. Scan Resources directory for Excel/CSV files
2. Extract team names from all cells
3. Normalize (strip whitespace, lowercase for dedup)
4. Apply keyword patterns to each team
5. Return deduplicated keyword list
"""

from __future__ import annotations

# Standard library imports
import os     # File and directory operations
import csv    # CSV file reading
from typing import List, Iterable  # Type hints


def _load_xlsx_keywords(xlsx_path: str) -> List[str]:
    try:
        import pandas as pd  # type: ignore
    except Exception:
        return []

    try:
        df = pd.read_excel(xlsx_path)
    except Exception:
        return []

    candidates: List[str] = []
    for col in df.columns:
        try:
            series = df[col].dropna().astype(str)
            candidates.extend(series.tolist())
        except Exception:
            continue
    return candidates


def _load_csv_keywords(csv_path: str) -> List[str]:
    keywords: List[str] = []
    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    cell = (cell or "").strip()
                    if cell:
                        keywords.append(cell)
    except Exception:
        return []
    return keywords


def _patterns_for(team: str) -> List[str]:
    team = (team or "").strip()
    if not team:
        return []
    return [
        f"{team} Tickets",
        f"{team} Ticket Exchange",
        f"{team} Verified Tickets",
        f"{team} Official Tickets",
    ]


def generate_keywords_from_resources(resources_dir: str = "Resources") -> List[str]:
    """
    Scan the resources directory for known files and produce a deduplicated list
    of search keywords by applying patterns.
    """
    teams: List[str] = []

    # Prefer known Excel file
    xlsx_path = os.path.join(resources_dir, "All Teams by Sport.xlsx")
    if os.path.exists(xlsx_path):
        teams.extend(_load_xlsx_keywords(xlsx_path))

    # Any CSV files in the directory
    if os.path.isdir(resources_dir):
        for name in os.listdir(resources_dir):
            if name.lower().endswith(".csv"):
                teams.extend(_load_csv_keywords(os.path.join(resources_dir, name)))

    # Fallback minimal list if nothing found
    if not teams:
        teams = [
            "Arizona Cardinals",
            "Atlanta Falcons",
            "Baltimore Ravens",
            "Buffalo Bills",
        ]

    # Normalize and deduplicate team names
    normalized = []
    seen = set()
    for t in teams:
        t = (t or "").strip()
        if not t:
            continue
        if t.lower() in seen:
            continue
        seen.add(t.lower())
        normalized.append(t)

    # Expand to keywords
    keywords: List[str] = []
    k_seen = set()
    for team in normalized:
        for k in _patterns_for(team):
            key = k.strip()
            if key.lower() in k_seen:
                continue
            k_seen.add(key.lower())
            keywords.append(key)

    return keywords


__all__ = [
    "generate_keywords_from_resources",
]



