import typer

app = typer.Typer(help="Configuration")


@app.command()
def show():
    typer.echo("Configuration")