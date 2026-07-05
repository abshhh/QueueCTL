import json

import typer
from rich.console import Console

from app.services.queue_service import QueueService

app = typer.Typer(help="Enqueue jobs", no_args_is_help=True)
console = Console()


def parse_payload(payload: str):
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(payload.encode().decode("unicode_escape"))
    except json.JSONDecodeError:
        pass

    stripped = payload.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        data = {}
        for item in stripped[1:-1].split(","):
            if ":" not in item:
                continue
            key, value = item.split(":", 1)
            data[key.strip().strip("\"'")] = value.strip().strip("\"'")
        if data:
            return data

    raise ValueError("payload must be valid JSON")


def create_job(command: str, job_id: str | None, max_retries: int | None):
    service = QueueService()

    try:
        job = service.enqueue(
            command=command,
            job_id=job_id,
            max_retries=max_retries,
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Job '{job.id}' queued successfully.[/bold green]")


@app.callback(invoke_without_command=True)
def enqueue(
    ctx: typer.Context,
    payload: str | None = typer.Argument(
        None,
        help='JSON payload, for example: {"id":"job1","command":"echo hello"}',
    ),
):
    """
    Add a JSON job payload to the queue.
    """

    if ctx.invoked_subcommand is not None:
        return

    if payload is None:
        console.print(ctx.get_help())
        raise typer.Exit()

    try:
        data = parse_payload(payload)
    except ValueError as exc:
        console.print(f"[bold red]Invalid payload:[/bold red] {exc}")
        raise typer.Exit(code=1)

    command = data.get("command")
    if not command:
        console.print("[bold red]Error:[/bold red] payload requires command")
        raise typer.Exit(code=1)

    create_job(
        command=command,
        job_id=data.get("id"),
        max_retries=data.get("max_retries"),
    )


@app.command()
def add(
    command: str = typer.Option(
        ...,
        "--command",
        "-c",
        help="Command to execute",
    ),
    job_id: str = typer.Option(
        None,
        "--id",
        help="Optional job ID",
    ),
    max_retries: int | None = typer.Option(
        None,
        "--max-retries",
        help="Maximum retry attempts (defaults to config value)",
    ),
):
    """
    Add a new job to the queue using flags.
    """

    create_job(command=command, job_id=job_id, max_retries=max_retries)
