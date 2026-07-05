import typer
from rich.console import Console
from rich.table import Table

from app.services.queue_service import QueueService

app = typer.Typer(help="Dead Letter Queue")

console = Console()

service = QueueService()


@app.command()
def list():

    jobs = service.list_dead_jobs()

    table = Table(title="Dead Letter Queue")

    table.add_column("ID")
    table.add_column("Attempts")
    table.add_column("Command")

    for job in jobs:

        table.add_row(
            job.id,
            str(job.attempts),
            job.command,
        )

    console.print(table)


@app.command()
def retry(job_id: str):

    job = service.retry_dead_job(job_id)

    if job is None:

        console.print(
            "[red]Job not found or not dead.[/red]"
        )

        raise typer.Exit(1)

    console.print(
        f"[green]Job {job.id} moved back to pending.[/green]"
    )