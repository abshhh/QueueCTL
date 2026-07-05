import typer

app = typer.Typer(help="Worker management")


@app.command()
def start():
    """Start worker(s)."""
    typer.echo("Worker started")


@app.command()
def stop():
    """Stop worker(s)."""
    typer.echo("Worker stopped")