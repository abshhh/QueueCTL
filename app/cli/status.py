import typer
from rich.console import Console
from rich.table import Table

from app.services.queue_service import QueueService

app = typer.Typer(help="Queue status")
console = Console()


def truncate(text: str | None, length: int = 40):
    if not text:
        return "-"

    text = text.strip()

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


@app.command()
def list():
    """
    List all jobs.
    """

    service = QueueService()

    jobs = service.list_jobs()

    table = Table(title="Queue Jobs")

    table.add_column("ID", style="cyan")
    table.add_column("State", style="green")
    table.add_column("Attempts", justify="center")
    table.add_column("Output")
    table.add_column("Error")

    for job in jobs:
        table.add_row(
            job.id,
            job.state,
            str(job.attempts),
            truncate(job.output),
            truncate(job.error),
        )

    console.print(table)


@app.command()
def show(job_id: str):
    """
    Show details for a single job.
    """

    service = QueueService()

    job = service.get_job(job_id)

    if job is None:
        console.print("[red]Job not found.[/red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]ID:[/bold] {job.id}")
    console.print(f"[bold]Command:[/bold] {job.command}")
    console.print(f"[bold]State:[/bold] {job.state}")
    console.print(f"[bold]Attempts:[/bold] {job.attempts}")
    console.print(f"[bold]Max Retries:[/bold] {job.max_retries}")

    console.print("\n[bold]Output[/bold]")
    console.print(job.output if job.output else "-")

    console.print("\n[bold]Error[/bold]")
    console.print(job.error if job.error else "-")