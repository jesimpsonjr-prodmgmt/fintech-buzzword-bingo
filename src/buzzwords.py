"""Utility helpers for the buzzword dictionary."""
import json
from pathlib import Path


def load_buzzwords(path: str = "data/buzzwords.json") -> dict:
    with open(path) as f:
        return json.load(f)


def all_terms(data: dict) -> list[str]:
    terms = []
    for cat_data in data["categories"].values():
        terms.extend(cat_data["terms"])
    terms.extend(data["bonus_phrases"]["terms"])
    return terms


def category_display_name(key: str) -> str:
    return key.replace("_", " ").title()
