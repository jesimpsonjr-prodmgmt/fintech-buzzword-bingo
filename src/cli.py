"""Fintech Buzzword Bingo — CLI entry point."""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich import box

from src.analyzer import BuzzwordAnalyzer, AnalysisResult, TERM_EMOJI, DEFAULT_EMOJI
from src.bingo_card import BingoCardGenerator
from src.buzzwords import category_display_name

console = Console()

BUZZWORDS_PATH = Path(__file__).parent.parent / "data" / "buzzwords.json"


def _get_analyzer() -> BuzzwordAnalyzer:
    return BuzzwordAnalyzer(str(BUZZWORDS_PATH))


def _score_bar(score: int, width: int = 30) -> str:
    filled = int(score / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    color = "green" if score < 40 else "yellow" if score < 70 else "red"
    return f"[{color}]{bar}[/{color}] {score}/100"


def _print_analysis(result: AnalysisResult, filename: str, verbose: bool = False):
    analyzer = _get_analyzer()

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]FINTECH BUZZWORD BINGO[/bold cyan]\n[dim]Analysis Report[/dim]",
            border_style="cyan",
        )
    )

    console.print(f"\n[bold]Document:[/bold] {filename}")
    console.print(f"[bold]Word Count:[/bold] {result.total_words:,}")
    console.print(f"[bold]Analysis Time:[/bold] {result.elapsed} seconds\n")

    score_color = "green" if result.final_score < 40 else "yellow" if result.final_score < 70 else "red"
    console.print(
        Panel(
            f"[bold {score_color}]BUZZWORD SCORE: {result.final_score} / 100[/bold {score_color}]\n"
            f"[dim]Rating:[/dim] [italic]\"{result.rating}\"[/italic]\n"
            f"{_score_bar(result.final_score)}",
            border_style=score_color,
        )
    )

    # Category breakdown
    console.print(Rule("[bold]CATEGORY BREAKDOWN[/bold]"))
    table = Table(show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("Category", style="cyan")
    table.add_column("Matches", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Top Terms")

    for cat, data in sorted(result.category_scores.items(), key=lambda x: x[1]["score"], reverse=True):
        top = ", ".join(f'"{t}" ({c})' for t, c in data["top_terms"][:2])
        table.add_row(
            category_display_name(cat),
            str(data["matches"]),
            str(data["score"]),
            top,
        )

    console.print(table)
    console.print(
        f"[bold]Total Buzzwords:[/bold] {result.total_buzzwords}   "
        f"[bold]Density:[/bold] {result.buzzword_density} per 1,000 words\n"
    )

    # Top offenders
    if result.top_terms:
        console.print(Rule("[bold]TOP OFFENDERS[/bold]"))
        for i, (term, count) in enumerate(result.top_terms[:5], 1):
            emoji = TERM_EMOJI.get(term.lower(), DEFAULT_EMOJI)
            console.print(f" {i}. [bold]\"{term}\"[/bold]  {count} occurrence{'s' if count != 1 else ''}  {emoji}")
        console.print()

    # Bonus phrases
    if result.bonus_phrases:
        console.print(Rule("[bold]BONUS PHRASES DETECTED[/bold]"))
        for phrase, count in result.bonus_phrases:
            console.print(f' • [yellow]"{phrase}"[/yellow] ({count} time{"s" if count != 1 else ""})')
        console.print()

    # Verbose: all matches
    if verbose and result.top_terms:
        console.print(Rule("[bold]ALL MATCHES[/bold]"))
        for term, count in result.top_terms:
            cat = _get_analyzer().term_to_category.get(term.lower(), "bonus")
            console.print(f"  [dim]{category_display_name(cat)}[/dim]  \"{term}\"  ×{count}")
        console.print()

    # Verdict
    console.print(Rule("[bold]VERDICT[/bold]"))
    verdict = analyzer.get_verdict(result, filename)
    console.print(f"[italic]{verdict}[/italic]")
    console.print(Rule())


@click.group()
def cli():
    """Fintech Buzzword Bingo — analyze corporate speak for maximum synergy."""


@cli.command()
@click.argument("file", required=False, type=click.Path(exists=True))
@click.option("--url", help="Fetch and analyze text from a URL")
@click.option("--verbose", "-v", is_flag=True, help="Show all matched terms")
@click.option("--chart", is_flag=True, help="Save a bar chart to output/")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON")
def analyze(file, url, verbose, chart, as_json):
    """Analyze a document or URL for buzzword density."""
    if not file and not url:
        raise click.UsageError("Provide a FILE path or --url.")

    if url:
        from src.scraper import fetch_text
        console.print(f"[dim]Fetching {url}...[/dim]")
        text = fetch_text(url)
        label = url
    else:
        with open(file) as f:
            text = f.read()
        label = file

    analyzer = _get_analyzer()
    result = analyzer.analyze(text)

    if as_json:
        output = {
            "document": label,
            "total_words": result.total_words,
            "total_buzzwords": result.total_buzzwords,
            "buzzword_density": result.buzzword_density,
            "final_score": result.final_score,
            "rating": result.rating,
            "category_scores": result.category_scores,
            "top_terms": result.top_terms,
            "bonus_phrases": result.bonus_phrases,
        }
        click.echo(json.dumps(output, indent=2))
        return

    _print_analysis(result, label, verbose=verbose)

    if chart:
        from src.visualizer import save_chart
        os.makedirs("output", exist_ok=True)
        chart_path = f"output/buzzword_chart_{date.today()}.png"
        save_chart(result, chart_path)
        console.print(f"\n[green]Chart saved to:[/green] {chart_path}")


@cli.command()
@click.option("--export", "-e", metavar="PATH", help="Export bingo card as HTML")
@click.option("--theme", default="earnings_call", show_default=True,
              help="Card theme label (for display only)")
def bingo(export, theme):
    """Generate a bingo card for your next earnings call or all-hands."""
    generator = BingoCardGenerator(str(BUZZWORDS_PATH))
    card = generator.generate_card()

    console.print()
    console.print(
        Panel.fit(
            f"[bold magenta]FINTECH BUZZWORD BINGO[/bold magenta]\n[dim]Theme: {theme}[/dim]",
            border_style="magenta",
        )
    )
    generator.print_card(card)

    if export:
        generator.export_html(card, export)
        console.print(f"\n[green]Saved to:[/green] {export}")
    else:
        answer = click.prompt("\nExport to HTML for printing? [y/N]", default="N")
        if answer.strip().lower() == "y":
            os.makedirs("output", exist_ok=True)
            out_path = f"output/bingo_card_{date.today()}.html"
            generator.export_html(card, out_path)
            console.print(f"[green]Saved to:[/green] {out_path}")


@cli.command()
@click.argument("file_a", type=click.Path(exists=True))
@click.argument("file_b", type=click.Path(exists=True))
def compare(file_a, file_b):
    """Compare two documents for buzzword density."""
    analyzer = _get_analyzer()

    with open(file_a) as f:
        text_a = f.read()
    with open(file_b) as f:
        text_b = f.read()

    result_a = analyzer.analyze(text_a)
    result_b = analyzer.analyze(text_b)

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]FINTECH BUZZWORD BINGO[/bold cyan]\n[dim]Document Comparison[/dim]",
            border_style="cyan",
        )
    )

    table = Table(show_header=True, header_style="bold", box=box.ROUNDED)
    table.add_column("Metric")
    table.add_column(Path(file_a).name, justify="right")
    table.add_column(Path(file_b).name, justify="right")
    table.add_column("Winner", justify="center")

    def winner(a, b, lower_is_better=False):
        if a == b:
            return "[dim]tie[/dim]"
        if lower_is_better:
            return f"[green]{Path(file_a).name}[/green]" if a < b else f"[green]{Path(file_b).name}[/green]"
        return f"[red]{Path(file_a).name}[/red]" if a > b else f"[red]{Path(file_b).name}[/red]"

    table.add_row("Word Count", f"{result_a.total_words:,}", f"{result_b.total_words:,}", "—")
    table.add_row("Total Buzzwords", str(result_a.total_buzzwords), str(result_b.total_buzzwords),
                  winner(result_a.total_buzzwords, result_b.total_buzzwords))
    table.add_row("Buzzword Density", f"{result_a.buzzword_density}/1k", f"{result_b.buzzword_density}/1k",
                  winner(result_a.buzzword_density, result_b.buzzword_density))
    table.add_row("Final Score", str(result_a.final_score), str(result_b.final_score),
                  winner(result_a.final_score, result_b.final_score))
    table.add_row("Rating", result_a.rating, result_b.rating, "—")

    console.print(table)

    # Bonus phrases comparison
    bp_a = {p for p, _ in result_a.bonus_phrases}
    bp_b = {p for p, _ in result_b.bonus_phrases}
    only_a = bp_a - bp_b
    only_b = bp_b - bp_a

    if only_a or only_b:
        console.print(Rule("[bold]UNIQUE BONUS PHRASES[/bold]"))
        if only_a:
            console.print(f"[cyan]{Path(file_a).name}[/cyan] only: " + ", ".join(f'"{p}"' for p in only_a))
        if only_b:
            console.print(f"[cyan]{Path(file_b).name}[/cyan] only: " + ", ".join(f'"{p}"' for p in only_b))

    console.print()
    if result_a.final_score > result_b.final_score:
        console.print(f"[bold red]{Path(file_a).name}[/bold red] wins the Buzzword Crown. Congratulations?")
    elif result_b.final_score > result_a.final_score:
        console.print(f"[bold red]{Path(file_b).name}[/bold red] wins the Buzzword Crown. Congratulations?")
    else:
        console.print("[bold]It's a tie![/bold] Both documents are equally synergistic.")
    console.print()


if __name__ == "__main__":
    cli()
