import typer
from rich.console import Console
from rich.table import Table

from app.services.queue_service import QueueService

app = typer.Typer(help="List jobs")

console = Console()


def truncate(text, length=35):

    if not text:
        return "-"

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


@app.callback(invoke_without_command=True)
def list_jobs(

    state: str = typer.Option(
        None,
        "--state",
        help="Filter by state",
    ),
):

    service = QueueService()

    if state:

        jobs = service.list_jobs_by_state(state)

    else:

        jobs = service.list_jobs()

    table = Table(title="Jobs")

    table.add_column("ID")
    table.add_column("State")
    table.add_column("Attempts")
    table.add_column("Retries")
    table.add_column("Command")

    for job in jobs:

        table.add_row(
            job.id,
            job.state,
            str(job.attempts),
            str(job.max_retries),
            truncate(job.command),
        )

    console.print(table)