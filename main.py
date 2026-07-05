import typer

from app.cli.enqueue import app as enqueue_app
from app.cli.worker import app as worker_app
from app.cli.status import app as status_app
from app.cli.dlq import app as dlq_app
from app.cli.config import app as config_app
from app.db.database import init_db
from app.cli.list_jobs import app as list_app
from app.cli.stats import app as stats_app



app = typer.Typer(
    help="QueueCTL - Production Style Background Job Queue",
    no_args_is_help=True,
)

app.add_typer(enqueue_app, name="enqueue")
app.add_typer(worker_app, name="worker")
app.add_typer(status_app, name="status")
app.add_typer(dlq_app, name="dlq")
app.add_typer(config_app, name="config")
app.add_typer(list_app, name="list")
app.add_typer(stats_app, name="stats")


@app.callback()
def main():
    """Initialize QueueCTL before running a command."""

    init_db()


@app.command()
def version():
    """Show QueueCTL version."""
    typer.echo("QueueCTL v0.1.0")


if __name__ == "__main__":
    app()
