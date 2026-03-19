"""Optional: fetch text content from a URL."""
from __future__ import annotations


def fetch_text(url: str) -> str:
    """Fetch plain text from a URL, stripping HTML tags."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise SystemExit(
            "Web scraping requires extra packages. Install them with:\n"
            "  pip install requests beautifulsoup4"
        )

    headers = {"User-Agent": "Mozilla/5.0 (compatible; fintech-buzzword-bingo/1.0)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script/style blocks
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)
