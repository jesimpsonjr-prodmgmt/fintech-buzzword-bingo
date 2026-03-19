"""Tests for BuzzwordAnalyzer."""
import pytest
from pathlib import Path

from src.analyzer import BuzzwordAnalyzer, RATINGS

BUZZWORDS_PATH = Path(__file__).parent.parent / "data" / "buzzwords.json"


@pytest.fixture
def analyzer():
    return BuzzwordAnalyzer(str(BUZZWORDS_PATH))


def test_clean_text_scores_zero(analyzer):
    text = "The quarterly revenue increased by fifteen percent year over year."
    result = analyzer.analyze(text)
    assert result.final_score == 0
    assert result.total_buzzwords == 0
    assert result.rating == "Refreshingly Jargon-Free"


def test_detects_ai_washing(analyzer):
    text = "Our AI-powered platform uses machine learning and deep learning to deliver intelligent solutions."
    result = analyzer.analyze(text)
    assert result.total_buzzwords >= 4
    assert "ai_washing" in result.category_scores


def test_detects_blockchain_buzzwords(analyzer):
    text = "We use blockchain and decentralized distributed ledger technology with tokenized assets."
    result = analyzer.analyze(text)
    assert "blockchain_buzzwords" in result.category_scores
    assert result.category_scores["blockchain_buzzwords"]["matches"] >= 3


def test_detects_bonus_phrases(analyzer):
    text = "We are customer-centric and data-driven. We don't want to boil the ocean."
    result = analyzer.analyze(text)
    phrase_names = [p for p, _ in result.bonus_phrases]
    assert "customer-centric" in phrase_names
    assert "data-driven" in phrase_names


def test_density_calculation(analyzer):
    # 10 words, 1 buzzword → density = 100 per 1k
    text = "We will disrupt this market with our innovative product this year"
    result = analyzer.analyze(text)
    assert result.buzzword_density > 0


def test_score_capped_at_100(analyzer):
    # Extremely buzzwordy text
    text = " ".join(
        ["AI-powered", "machine learning", "blockchain", "decentralized", "disrupt",
         "transform", "seamless", "frictionless", "synergy", "ecosystem",
         "leverage", "scale", "hypergrowth", "flywheel", "data-driven",
         "customer-centric", "north star metric", "move the needle"] * 5
    )
    result = analyzer.analyze(text)
    assert result.final_score <= 100


def test_rating_ranges():
    for low, high, name, desc in RATINGS:
        assert low <= high
        assert isinstance(name, str)
        assert isinstance(desc, str)


def test_top_terms_sorted_by_count(analyzer):
    text = "seamless seamless seamless AI-powered AI-powered blockchain"
    result = analyzer.analyze(text)
    if len(result.top_terms) >= 2:
        assert result.top_terms[0][1] >= result.top_terms[1][1]


def test_word_count(analyzer):
    text = "Hello world this is a test with eight words here"
    result = analyzer.analyze(text)
    assert result.total_words == 10


def test_case_insensitive(analyzer):
    text_lower = "our platform is ai-powered and uses machine learning"
    text_upper = "OUR PLATFORM IS AI-POWERED AND USES MACHINE LEARNING"
    result_lower = analyzer.analyze(text_lower)
    result_upper = analyzer.analyze(text_upper)
    assert result_lower.total_buzzwords == result_upper.total_buzzwords


def test_empty_text(analyzer):
    result = analyzer.analyze("")
    assert result.total_words == 0
    assert result.total_buzzwords == 0
    assert result.final_score == 0
