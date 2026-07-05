import typer
from rich.console import Console

from app.services.queue_service import QueueService

app = typer.Typer(help="Enqueue jobs")
console = Console()


@app.command()
def add(
    command: str = typer.Option(
        ...,
        "--command",
        "-c",
        help="Command to execute",
    ),
    job_id: str = typer.Option(
        None,
        "--id",
        help="Optional job ID",
    ),
    max_retries: int | None = typer.Option(
        None,
        "--max-retries",
        help="Maximum retry attempts (defaults to config value)",
    ),
):
    """
    Add a new job to the queue.
    """

    service = QueueService()

    try:

        job = service.enqueue(
            command=command,
            job_id=job_id,
            max_retries=max_retries,
        )

        console.print(
            f"[bold green]✓ Job '{job.id}' queued successfully.[/bold green]"
        )

    except Exception as e:

        console.print(
            f"[bold red]Error:[/bold red] {e}"
        )

        raise typer.Exit(code=1)