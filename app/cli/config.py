import typer
from rich.console import Console
from rich.table import Table

from app.core.settings import Settings

app = typer.Typer(help="Configuration")

console = Console()

settings = Settings()


@app.command()
def show():

    settings.reload()

    table = Table(title="QueueCTL Configuration")

    table.add_column("Key")
    table.add_column("Value")

    for key, value in settings.config.items():

        table.add_row(
            key,
            str(value),
        )

    console.print(table)


@app.command()
def set(
    key: str,
    value: str,
):

    settings.reload()
    key = key.replace("-", "_")

    if key not in settings.config:

        console.print(
            f"[red]Unknown configuration key: {key}[/red]"
        )

        raise typer.Exit(1)

    current = settings.get(key)

    if isinstance(current, int):
        value = int(value)

    settings.set(key, value)

    console.print(
        f"[green]{key} updated to {value}[/green]"
    )
