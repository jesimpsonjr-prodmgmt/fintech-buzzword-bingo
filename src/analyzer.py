from dataclasses import dataclass, field
from collections import Counter
import re
import json
import time


@dataclass
class AnalysisResult:
    total_words: int
    total_buzzwords: int
    buzzword_density: float
    category_scores: dict
    top_terms: list
    bonus_phrases: list
    final_score: int
    rating: str
    rating_desc: str
    elapsed: float = 0.0


RATINGS = [
    (0, 20, "Refreshingly Jargon-Free", "Either a technical doc or someone who respects their audience."),
    (21, 40, "Mildly Buzzwordy", "Some corporate speak, but mostly tolerable."),
    (41, 60, "Getting Buzzed", "Marketing had input on this one."),
    (61, 80, "Peak Synergy", "This document is leveraging best-in-class buzzword density."),
    (81, 100, "Full Bingo", "Did an AI write this? Actually, an AI would be more subtle."),
]

# Emoji mapping for top offenders display
TERM_EMOJI = {
    "ai-powered": "🤖", "machine learning": "🤖", "deep learning": "🤖", "neural": "🤖",
    "intelligent": "🧠", "cognitive": "🧠", "predictive": "🧠", "autonomous": "🤖",
    "blockchain": "⛓️", "decentralized": "⛓️", "distributed ledger": "⛓️",
    "web3": "⛓️", "tokenized": "🪙", "on-chain": "⛓️", "trustless": "⛓️",
    "seamless": "✨", "frictionless": "✨", "ecosystem": "🌳",
    "transform": "🔄", "disrupt": "💥", "revolutionize": "💥",
    "scale": "📈", "hypergrowth": "🚀", "flywheel": "🔁", "viral": "🦠",
    "synergy": "🤝", "leverage": "💪",
}

DEFAULT_EMOJI = "💬"


class BuzzwordAnalyzer:
    def __init__(self, buzzwords_path: str = "data/buzzwords.json"):
        with open(buzzwords_path) as f:
            self.buzzwords = json.load(f)

        self.term_to_category = {}
        self.category_weights = {}

        for category, data in self.buzzwords["categories"].items():
            self.category_weights[category] = data["weight"]
            for term in data["terms"]:
                self.term_to_category[term.lower()] = category

        self.bonus_phrases = [p.lower() for p in self.buzzwords["bonus_phrases"]["terms"]]

    def analyze(self, text: str) -> AnalysisResult:
        start = time.time()
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)

        term_counts = Counter()
        category_counts = Counter()

        for term, category in self.term_to_category.items():
            count = len(re.findall(r'\b' + re.escape(term) + r'\b', text_lower))
            if count > 0:
                term_counts[term] = count
                category_counts[category] += count

        bonus_found = []
        for phrase in self.bonus_phrases:
            count = text_lower.count(phrase)
            if count > 0:
                bonus_found.append((phrase, count))

        category_scores = {}
        total_score = 0

        for category, count in category_counts.items():
            weight = self.category_weights[category]
            score = count * weight
            top_terms = sorted(
                [(term, c) for term, c in term_counts.items()
                 if self.term_to_category.get(term) == category],
                key=lambda x: x[1],
                reverse=True
            )[:3]
            category_scores[category] = {
                "matches": count,
                "score": score,
                "top_terms": top_terms,
            }
            total_score += score

        bonus_score = sum(count * 5 for _, count in bonus_found)
        total_score += bonus_score

        total_buzzwords = sum(term_counts.values())
        density = (total_buzzwords / total_words * 1000) if total_words > 0 else 0

        final_score = min(100, int(total_score * (1 + density / 10)))

        rating = "Unknown"
        rating_desc = ""
        for low, high, name, desc in RATINGS:
            if low <= final_score <= high:
                rating = name
                rating_desc = desc
                break

        elapsed = time.time() - start

        return AnalysisResult(
            total_words=total_words,
            total_buzzwords=total_buzzwords,
            buzzword_density=round(density, 2),
            category_scores=category_scores,
            top_terms=term_counts.most_common(10),
            bonus_phrases=bonus_found,
            final_score=final_score,
            rating=rating,
            rating_desc=rating_desc,
            elapsed=round(elapsed, 2),
        )

    def get_verdict(self, result: AnalysisResult, filename: str = "") -> str:
        lines = []
        lines.append(f"This document achieved {result.rating.upper()} on the buzzword scale.")
        lines.append("")

        if result.top_terms:
            top_term, top_count = result.top_terms[0]
            if top_term in ("ai-powered", "machine learning", "deep learning"):
                lines.append(
                    f'The heavy use of "{top_term}" ({top_count} times) suggests either genuine AI\n'
                    'capabilities or a marketing team that recently discovered ChatGPT.'
                )
            elif top_term in ("blockchain", "decentralized", "web3"):
                lines.append(
                    f'"{top_term}" appears {top_count} times. Whether there\'s actual blockchain\n'
                    'technology here or just blockchain vibes remains unclear.'
                )
            else:
                lines.append(
                    f'"{top_term}" leads the pack with {top_count} occurrences.\n'
                    'Whoever wrote this has a type.'
                )

        if result.top_terms:
            drink_term = result.top_terms[0][0]
            lines.append("")
            lines.append(
                f'Recommendation: Take a drink every time someone says "{drink_term}"\n'
                'during the actual meeting. (Please drink responsibly.)'
            )

        return "\n".join(lines)
