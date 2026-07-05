# QueueCTL

QueueCTL is a CLI-based persistent background job queue. It can enqueue shell
commands, run one or more workers, retry failed jobs with exponential backoff,
and move exhausted jobs into a Dead Letter Queue (DLQ).

## Features

- Persistent SQLite job storage
- CLI for enqueueing, listing, status, config, workers, and DLQ operations
- Multiple worker threads with SQLite row claiming to avoid duplicate work
- Automatic retry with exponential backoff
- Dead Letter Queue for permanently failed jobs
- Configurable retry count, backoff base, and polling interval
- Minimal tests for enqueueing, worker processing, locking, retry, and DLQ

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run commands with:

```powershell
python main.py --help
```

Optional editable install:

```powershell
pip install -e .
queuectl --help
```

## Usage

Enqueue a job using the assignment-style JSON payload:

```powershell
python main.py enqueue '{"id":"job1","command":"echo hello"}'
```

Alternative flag-based enqueue:

```powershell
python main.py enqueue add --id job2 --command "python -c `"print('hello')`" --max-retries 3
```

Start three workers:

```powershell
python main.py worker start --count 3
```

Stop workers gracefully:

```powershell
python main.py worker stop
```

Show queue status:

```powershell
python main.py status
```

List all jobs:

```powershell
python main.py list
```

List jobs by state:

```powershell
python main.py list --state failed
python main.py list --state dead
```

View DLQ jobs:

```powershell
python main.py dlq list
```

Retry a DLQ job:

```powershell
python main.py dlq retry job1
```

Show configuration:

```powershell
python main.py config show
```

Update configuration:

```powershell
python main.py config set max-retries 3
python main.py config set backoff_base 2
python main.py config set poll_interval 1
```

## Architecture

Jobs are stored in SQLite at `data/queue.db`. Each job has an ID, command,
state, attempt count, retry limit, timestamps, output, error, and lock owner.

The job lifecycle is:

```text
pending -> processing -> completed
pending -> processing -> failed -> processing -> dead
```

When a worker polls, it claims one available `pending` or retryable `failed`
job whose `next_run_at` has arrived. Claiming uses an atomic SQLite
`UPDATE ... RETURNING` inside `BEGIN IMMEDIATE`, so concurrent workers do not
pick the same job.

Workers run commands with the local shell. Exit code `0` marks a job
`completed`. Non-zero exit codes increment `attempts`. If attempts are below
`max_retries`, QueueCTL marks the job `failed` and schedules it using:

```text
delay = backoff_base ^ attempts seconds
```

Once attempts reach `max_retries`, the job moves to `dead` and appears in the
DLQ.

Configuration lives in `config.json`, and worker heartbeats live in
`data/workers.json` so `status` can report active workers.

## Testing

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Current tests cover:

- Enqueueing a job
- Worker completing a successful command
- Failed job moving to DLQ
- Retry scheduling with exponential backoff
- DLQ retry
- Duplicate-claim prevention for workers

## Assumptions and Trade-offs

- SQLite is used because it is embedded, persistent, easy to review, and
  enough for a take-home queue assignment.
- `worker stop` creates a local stop signal. Workers check it between jobs and
  exit after finishing the job currently in progress.
- Workers are threads inside one CLI process when `--count` is greater than 1.
  Separate terminals can also run workers against the same SQLite database.
- Commands are executed with `shell=True` to match the assignment examples
  like `sleep 2` and `echo hello`. In a production multi-tenant system this
  would need sandboxing and stricter validation.
- Job output and errors are stored on the job row for easier debugging.

## Demo Recording

The assignment asks for a recorded CLI demo link in the README. Record a short
demo showing enqueue, worker processing, retry/DLQ, and status, upload it to
Drive, and paste the link here before submission.
