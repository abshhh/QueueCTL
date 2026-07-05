import typer
from rich.console import Console
from rich.table import Table

from app.services.queue_service import QueueService

app = typer.Typer(help="Queue status")
console = Console()


@app.command()
def list():
    """
    List all jobs.
    """

    service = QueueService()
    jobs = service.list_jobs()

    table = Table(title="Jobs")

    table.add_column("ID")
    table.add_column("Command")
    table.add_column("State")
    table.add_column("Attempts")

    for job in jobs:
        table.add_row(
            job.id,
            job.command,
            job.state,
            str(job.attempts),
        )

    console.print(table)