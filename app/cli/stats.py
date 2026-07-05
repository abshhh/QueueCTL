import typer
from rich.console import Console
from rich.table import Table

from app.db.database import SessionLocal
from app.db.repository import JobRepository
from app.services.worker_registry import WorkerRegistry

app = typer.Typer(help="Queue statistics")

console = Console()


@app.command()
def show():
    """
    Display queue statistics.
    """

    db = SessionLocal()

    try:

        repository = JobRepository(db)

        stats = repository.stats()

        registry = WorkerRegistry()

        table = Table(title="Queue Statistics")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Total Jobs", str(stats["total"]))
        table.add_row("Pending", str(stats["pending"]))
        table.add_row("Processing", str(stats["processing"]))
        table.add_row("Completed", str(stats["completed"]))
        table.add_row("Failed", str(stats["failed"]))
        table.add_row("Dead", str(stats["dead"]))

        table.add_section()

        table.add_row(
            "Average Retries",
            str(stats["average_retries"]),
        )

        table.add_row(
            "Max Retries Used",
            str(stats["max_retries_used"]),
        )

        table.add_section()

        table.add_row(
            "Active Workers",
            str(len(registry.active_workers())),
        )

        console.print(table)

    finally:

        db.close()