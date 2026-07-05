from datetime import datetime

from app.db.repository import JobRepository
from app.services.worker_service import WorkerService


def test_worker_completes_successful_job(temp_db, monkeypatch):
    db = temp_db()
    repo = JobRepository(db)
    repo.create("ok-job", "echo hello", 3)
    db.close()

    monkeypatch.setattr("app.services.worker_service.SessionLocal", temp_db)

    result = WorkerService().process_next_job()

    db = temp_db()
    job = JobRepository(db).get("ok-job")

    assert result["type"] == "success"
    assert job.state == "completed"
    assert "hello" in job.output.lower()
    assert job.locked_by is None

    db.close()


def test_failed_job_moves_to_dlq_after_retries(temp_db, monkeypatch):
    db = temp_db()
    repo = JobRepository(db)
    repo.create(
        "bad-job",
        'python -c "import sys; sys.exit(7)"',
        1,
    )
    db.close()

    monkeypatch.setattr("app.services.worker_service.SessionLocal", temp_db)

    result = WorkerService().process_next_job()

    db = temp_db()
    job = JobRepository(db).get("bad-job")

    assert result["type"] == "dead"
    assert job.state == "dead"
    assert job.attempts == 1
    assert job.locked_by is None

    db.close()


def test_failed_job_uses_exponential_backoff(temp_db, monkeypatch):
    db = temp_db()
    repo = JobRepository(db)
    repo.create(
        "retry-job",
        'python -c "import sys; sys.exit(7)"',
        3,
    )
    db.close()

    monkeypatch.setattr("app.services.worker_service.SessionLocal", temp_db)

    before = datetime.utcnow()
    result = WorkerService().process_next_job()

    db = temp_db()
    job = JobRepository(db).get("retry-job")

    assert result["type"] == "retry"
    assert result["delay"] == 2
    assert job.state == "failed"
    assert job.attempts == 1
    assert job.next_run_at > before

    db.close()
