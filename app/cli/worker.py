import threading

import typer
from rich.console import Console

from app.services.worker_service import WorkerService

app = typer.Typer(help="Worker management")

console = Console()


def worker_loop(worker_id: int, stop_event: threading.Event):

    console.print(
        f"[cyan]Worker-{worker_id} started[/cyan]"
    )

    worker = WorkerService()

    worker.start(stop_event)


@app.command()
def start(
    count: int = typer.Option(
        1,
        "--count",
        "-c",
        help="Number of workers",
    ),
):
    """
    Start one or more workers.
    """

    console.print(
        f"[bold green]Starting {count} worker(s)...[/bold green]"
    )

    stop_event = threading.Event()

    threads = []

    for i in range(count):

        thread = threading.Thread(
            target=worker_loop,
            args=(i + 1, stop_event),
        )

        thread.start()

        threads.append(thread)

    try:

        while True:
            thread = threads[0]
            thread.join(timeout=0.5)

    except KeyboardInterrupt:

        console.print(
            "\n[yellow]Stopping workers...[/yellow]"
        )

        stop_event.set()

        for thread in threads:
            thread.join()

        console.print(
            "[green]All workers stopped gracefully.[/green]"
        )


@app.command()
def stop():
    """
    Placeholder.
    """

    console.print(
        "[yellow]Press Ctrl+C in the worker terminal to stop workers.[/yellow]"
    )