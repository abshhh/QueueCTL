import typer

app = typer.Typer(help="Enqueue jobs")


@app.command()
def add():
    """Add a new job to the queue."""
    typer.echo("Enqueue command")