"""Chart generation for buzzword analysis results."""
from __future__ import annotations
import os

from src.analyzer import AnalysisResult
from src.buzzwords import category_display_name


def save_chart(result: AnalysisResult, output_path: str):
    """Save a bar chart of category scores to output_path."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        raise SystemExit(
            "matplotlib is required for chart output. Install it with: pip install matplotlib"
        )

    if not result.category_scores:
        raise ValueError("No buzzword data to chart.")

    categories = list(result.category_scores.keys())
    scores = [result.category_scores[c]["score"] for c in categories]
    labels = [category_display_name(c) for c in categories]

    colors = [
        "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6", "#1abc9c"
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels, scores, color=colors[: len(labels)], edgecolor="white", linewidth=0.8)

    ax.set_xlabel("Weighted Score", fontsize=12)
    ax.set_title(
        f"Fintech Buzzword Analysis\nOverall Score: {result.final_score}/100 — {result.rating}",
        fontsize=13,
        fontweight="bold",
    )

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height() / 2,
            str(score),
            va="center",
            fontsize=10,
        )

    ax.set_xlim(0, max(scores) * 1.2 if scores else 10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
