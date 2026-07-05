import typer
from rich.console import Console

from app.services.worker_service import WorkerService

app = typer.Typer(help="Worker management")

console = Console()


@app.command()
def start():
    """
    Execute one pending job.
    """

    worker = WorkerService()

    result = worker.run_once()

    if result is None:
        console.print("[yellow]No pending jobs.[/yellow]")
        raise typer.Exit()

    console.print("[bold green]✓ Job executed[/bold green]\n")
    console.print(f"ID        : {result['id']}")
    console.print(f"State     : {result['state']}")
    console.print(f"Exit Code : {result['exit_code']}")


@app.command()
def stop():
    """
    Placeholder for graceful shutdown.
    """

    console.print("[yellow]Worker stopped.[/yellow]")