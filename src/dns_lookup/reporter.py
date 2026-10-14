"""Rich terminal reporter for DNS results."""

from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

console = Console()

# Colors per record type for visual grouping
TYPE_COLORS = {
    "A": "green",
    "AAAA": "bright_green",
    "CNAME": "cyan",
    "MX": "yellow",
    "NS": "magenta",
    "TXT": "white",
    "SOA": "bright_cyan",
}


def print_report(name: str, results: dict) -> None:
    """Print results as one table per record type."""
    console.print()
    console.rule(f"[bold cyan]DNS Lookup: {name}[/bold cyan]")

    if not results:
        console.print("[yellow]No records found.[/yellow]")
        return

    for rdtype, values in results.items():
        color = TYPE_COLORS.get(rdtype, "white")
        table = Table(
            title=f"[{color}]{rdtype}[/{color}]",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Value", style="white", overflow="fold")

        for value in values:
            table.add_row(value)

        console.print(table)

    total = sum(len(v) for v in results.values())
    console.print(
        f"\n[bold]{total} record(s)[/bold] across "
        f"[bold]{len(results)}[/bold] type(s)."
    )


def to_json(name: str, results: dict) -> str:
    """Serialize results as JSON."""
    payload = {
        "name": name,
        "records": results,
        "total": sum(len(v) for v in results.values()),
    }
    return json.dumps(payload, indent=2)
