import typer

app = typer.Typer(help="Dead Letter Queue")


@app.command()
def list():
    typer.echo("DLQ list")


@app.command()
def retry(job_id: str):
    typer.echo(f"Retrying {job_id}")