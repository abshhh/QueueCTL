import typer
from rich.console import Console
from datetime import datetime  , timedelta

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

    priority: int = typer.Option(
        0,
        "--priority",
        "-p",
        help="Higher values are processed first.",
    ),


    delay: int | None = typer.Option(
        None,
        "--delay",
        help="Delay execution by N seconds.",
    ),

    run_at: str | None = typer.Option(
        None,
        "--run-at",
        help="Schedule execution at ISO format (YYYY-MM-DDTHH:MM:SS).",
    ),


):
    """
    Add a new job to the queue.
    """

    scheduled_time = None

    if run_at is not None:
        try:
            scheduled_time = datetime.fromisoformat(run_at)
        except ValueError:
            console.print(
                "[bold red]Invalid datetime format.[/bold red]"
            )
            raise typer.Exit(1)


    service = QueueService()

    try:
        job = service.enqueue(
            command=command,
            job_id=job_id,
            max_retries=max_retries,
            priority = priority,
            delay = delay,
            run_at = scheduled_time,
        )

        console.print(
            f"[bold green]Job '{job.id}' queued successfully.[/bold green]"
        )

    except Exception as e:
        console.print(
            f"[bold red]Error:[/bold red] {e}"
        )
        raise typer.Exit(code=1)