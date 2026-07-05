import typer

app = typer.Typer(help="Queue status")


@app.command()
def show():
    typer.echo("Queue status")