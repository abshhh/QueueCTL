import threading
import typer
from rich.console import Console

from app.services.worker_service import WorkerService

app = typer.Typer(help="Worker management")

console = Console()


def worker_loop(worker_id: int):
    console.print(f"[cyan]Worker-{worker_id} started[/cyan]")

    worker = WorkerService()
    worker.start()


@app.command()
def start(
    count: int = typer.Option(
        1,
        "--count",
        "-c",
        help="Number of workers to start",
    ),
):
    """
    Start one or more workers.
    """

    console.print(
        f"[bold green]Starting {count} worker(s)...[/bold green]"
    )

    threads = []

    for i in range(count):

        thread = threading.Thread(
            target=worker_loop,
            args=(i + 1,),
            daemon=True,
        )

        thread.start()
        threads.append(thread)

    try:
        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Stopping all workers gracefully...[/yellow]"
        )


@app.command()
def stop():
    """
    Placeholder for graceful shutdown.
    """

    console.print(
        "[yellow]Stop the running worker(s) using Ctrl+C.[/yellow]"
    )