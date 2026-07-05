import typer
from rich.console import Console
from rich.table import Table

from app.services.queue_service import QueueService

app = typer.Typer(help="Queue summary")

console = Console()


@app.callback(invoke_without_command=True)
def status():

    service = QueueService()

    summary = service.get_summary()

    table = Table(title="Queue Summary")

    table.add_column("State")
    table.add_column("Count", justify="right")

    table.add_row("Pending", str(summary["pending"]))
    table.add_row("Processing", str(summary["processing"]))
    table.add_row("Completed", str(summary["completed"]))
    table.add_row("Dead", str(summary["dead"]))
    table.add_row("Total", str(summary["total"]))

    console.print(table)