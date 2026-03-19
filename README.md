# Fintech Buzzword Bingo

A tongue-in-cheek Python tool that analyzes earnings calls, press releases, and corporate communications for buzzword density. Because sometimes you need to quantify the synergy.

## Why I Built This

After 20+ years in fintech, I've sat through countless earnings calls and read thousands of press releases. I noticed patterns. "AI-powered" started appearing everywhere around 2023. "Blockchain" peaked in 2021. "Seamless" never goes out of style.

This tool is partly a joke and partly a genuine text analysis exercise. It demonstrates NLP basics, scoring algorithms, and visualization while poking fun at corporate speak.

## Features

- **Analyze documents** for buzzword density and category breakdown
- **Generate bingo cards** for your next earnings call or all-hands meeting
- **Compare documents** to see who's more buzzwordy
- **Visualize trends** with category score charts

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/fintech-buzzword-bingo.git
cd fintech-buzzword-bingo
pip install -r requirements.txt
```

## Usage

### Analyze a Document

```bash
python -m src.cli analyze data/sample_transcript.txt
python -m src.cli analyze earnings_call.txt --verbose
python -m src.cli analyze earnings_call.txt --chart
python -m src.cli analyze earnings_call.txt --json
```

### Analyze from a URL

```bash
python -m src.cli analyze --url "https://example.com/press-release"
```

### Generate a Bingo Card

```bash
python -m src.cli bingo
python -m src.cli bingo --export output/bingo_card.html
```

### Compare Two Documents

```bash
python -m src.cli compare q1_earnings.txt q2_earnings.txt
```

## Scoring System

Documents are scored on a 0–100 scale based on:
- Total buzzword count
- Buzzword density (per 1,000 words)
- Category weights (AI-washing scores higher than generic corporate speak)
- Bonus phrase detection

### Ratings

| Score | Rating | Description |
|-------|--------|-------------|
| 0–20 | Refreshingly Jargon-Free | Someone respects their audience |
| 21–40 | Mildly Buzzwordy | Mostly tolerable |
| 41–60 | Getting Buzzed | Marketing had input |
| 61–80 | Peak Synergy | Best-in-class buzzword density |
| 81–100 | Full Bingo | Did an AI write this? |

## Buzzword Categories

| Category | Weight | Examples |
|----------|--------|---------|
| AI Washing | 3× | AI-powered, machine learning, cognitive |
| Blockchain Buzzwords | 3× | decentralized, web3, tokenized |
| Innovation Theater | 2× | disrupt, transform, paradigm shift |
| Synergy Bingo | 2× | ecosystem, leverage, seamless |
| Vague Promises | 2× | robust, enterprise-grade, state-of-the-art |
| Growth Speak | 1× | scale, flywheel, hypergrowth |
| Payments Jargon | 1× | embedded finance, omnichannel, super app |

## Running Tests

```bash
pytest tests/
```

## Project Structure

```
fintech-buzzword-bingo/
├── src/
│   ├── cli.py          # CLI entry point (click)
│   ├── analyzer.py     # Scoring and analysis logic
│   ├── bingo_card.py   # Bingo card generation + HTML export
│   ├── buzzwords.py    # Buzzword dictionary helpers
│   ├── visualizer.py   # matplotlib bar charts
│   └── scraper.py      # URL fetching (requests + BeautifulSoup)
├── data/
│   ├── buzzwords.json  # Buzzword definitions and categories
│   └── sample_transcript.txt
├── tests/
│   └── test_analyzer.py
└── output/             # Generated charts and HTML cards
```

## Contributing

Found a buzzword I missed? Open a PR to add it to `data/buzzwords.json`.

## Disclaimer

This is satire. No corporations were harmed in the making of this tool. (Their earnings calls were already like this.)

## License

MIT
