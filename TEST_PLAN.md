# QueueCTL Test Cases

This document describes the manual and automated test cases used to validate QueueCTL.

---

# Test 1 — Basic Job Execution

## Objective

Verify that a simple job executes successfully.

## Command

```bash
python main.py enqueue add \
    --id job1 \
    --command "echo Hello"
```

Start worker

```bash
python main.py worker start
```

## Expected Result

- Worker claims job
- Command executes
- Exit code = 0
- Job state → `completed`

---

# Test 2 — Invalid Command

## Objective

Verify failed commands retry automatically.

## Command

```bash
python main.py enqueue add \
    --command "invalid_command"
```

## Expected Result

```
pending

↓

processing

↓

failed

↓

pending

↓

processing

↓

dead
```

Retry delay follows

```
base ^ attempts
```

---

# Test 3 — Exponential Backoff

## Configuration

```json
{
    "backoff_base": 2
}
```

## Expected Delays

| Attempt | Delay |
|----------|-------|
| 1 | 2 sec |
| 2 | 4 sec |
| 3 | 8 sec |

---

# Test 4 — Dead Letter Queue

## Objective

Verify jobs move into the DLQ.

Command

```bash
python main.py dlq list
```

Expected

```
job1
job2
job3
```

Retry

```bash
python main.py dlq retry job1
```

Expected

```
State

dead

↓

pending
```

---

# Test 5 — Multiple Workers

Start

```bash
python main.py worker start --count 4
```

Expected

- Four workers start
- Jobs processed in parallel
- No duplicate execution

---

# Test 6 — Duplicate Processing Prevention

## Objective

Verify atomic locking.

Implementation

```sql
BEGIN IMMEDIATE

UPDATE ...

RETURNING
```

Expected

Worker A

```
claims job
```

Worker B

```
receives None
```

No duplicate processing occurs.

---

# Test 7 — Persistence

Enqueue

```bash
python main.py enqueue add \
    --command "sleep 30"
```

Stop application.

Restart.

Expected

Job still exists in SQLite.

---

# Test 8 — Priority Queue

Enqueue

```bash
python main.py enqueue add \
    --id low \
    --priority 1 \
    --command "echo LOW"

python main.py enqueue add \
    --id high \
    --priority 10 \
    --command "echo HIGH"
```

Expected Execution

```
HIGH

↓

LOW
```

---

# Test 9 — Scheduled Jobs

Delay

```bash
python main.py enqueue add \
    --delay 30 \
    --command "echo Hello"
```

Expected

Worker ignores job until

```
next_run_at <= current_time
```

Then executes automatically.

---

# Test 10 — Dashboard

Launch

```bash
streamlit run dashboard.py
```

Expected

- Queue metrics visible
- Active worker count
- Job table
- Retry chart
- State chart
- Search
- Filters
- Auto refresh

---

# Automated Tests

Execute

```bash
pytest -q
```

Current automated coverage

- Enqueue
- Worker success
- Retry
- DLQ
- DLQ retry
- Atomic locking

Expected

```
====== 6 passed ======
```

---

# End-to-End Validation

Run

```bash
python main.py enqueue add --command "echo Demo"

python main.py worker start --count 3

python main.py status

python main.py list

python main.py dlq list

streamlit run dashboard.py
```

Expected

✔ Job executes

✔ Dashboard updates

✔ Worker count visible

✔ Queue state updated

✔ No duplicate processing