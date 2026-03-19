import random
from datetime import date
from rich.console import Console
from rich.table import Table
import json


class BingoCardGenerator:
    def __init__(self, buzzwords_path: str = "data/buzzwords.json"):
        with open(buzzwords_path) as f:
            data = json.load(f)

        self.all_terms = []
        for cat_data in data["categories"].values():
            self.all_terms.extend(cat_data["terms"])
        self.all_terms.extend(data["bonus_phrases"]["terms"])

    def generate_card(self, size: int = 5) -> list[list[str]]:
        terms_needed = size * size
        if size == 5:
            terms_needed -= 1  # center is FREE

        selected = random.sample(self.all_terms, min(terms_needed, len(self.all_terms)))

        card = []
        idx = 0
        for row in range(size):
            card_row = []
            for col in range(size):
                if size == 5 and row == 2 and col == 2:
                    card_row.append("FREE\n(synergy)")
                else:
                    card_row.append(selected[idx])
                    idx += 1
            card.append(card_row)

        return card

    def print_card(self, card: list[list[str]]):
        console = Console()

        table = Table(
            title="[bold magenta]FINTECH BUZZWORD BINGO[/bold magenta]",
            show_header=True,
            header_style="bold magenta",
            border_style="magenta",
        )

        for letter in "BINGO":
            table.add_column(letter, justify="center", width=16)

        for row in card:
            table.add_row(*[self._format_cell(cell) for cell in row])

        console.print(table)
        console.print("\n[dim]Mark a square when you hear the term. First to five in a row wins![/dim]")

    def _format_cell(self, text: str) -> str:
        if "FREE" in text:
            return "[bold green]FREE[/bold green]\n[dim](synergy)[/dim]"
        # Wrap long terms
        if len(text) > 14:
            words = text.split()
            mid = len(words) // 2
            return " ".join(words[:mid]) + "\n" + " ".join(words[mid:])
        return text

    def export_html(self, card: list[list[str]], output_path: str):
        rows_html = ""
        for row in card:
            rows_html += "<tr>"
            for cell in row:
                css_class = "free" if "FREE" in cell else ""
                display = "FREE<br><small>(synergy)</small>" if "FREE" in cell else cell.replace("\n", "<br>")
                rows_html += f'<td class="{css_class}">{display}</td>'
            rows_html += "</tr>"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fintech Buzzword Bingo</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
        h1 {{ text-align: center; color: #333; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; margin: 0 auto; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        td {{
            border: 2px solid #4A90D9;
            width: 120px;
            height: 100px;
            text-align: center;
            vertical-align: middle;
            padding: 10px;
            font-size: 12px;
            line-height: 1.4;
        }}
        .free {{ background: #90EE90; font-weight: bold; font-size: 14px; }}
        .header {{ background: #4A90D9; color: white; font-weight: bold; font-size: 24px; height: 50px; }}
        p.note {{ text-align: center; color: #666; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Fintech Buzzword Bingo</h1>
    <p class="subtitle">Generated {date.today().strftime("%B %d, %Y")}</p>
    <table>
        <tr>
            <td class="header">B</td>
            <td class="header">I</td>
            <td class="header">N</td>
            <td class="header">G</td>
            <td class="header">O</td>
        </tr>
        {rows_html}
    </table>
    <p class="note">Mark a square when you hear the term. First to five in a row wins!</p>
</body>
</html>
"""
        with open(output_path, "w") as f:
            f.write(html)
