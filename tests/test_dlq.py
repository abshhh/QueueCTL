from datetime import datetime

from app.db.repository import JobRepository


def test_retry_dead_job(temp_db):

    db = temp_db()

    repo = JobRepository(db)

    job = repo.create(
        "deadjob",
        "invalid",
        3,
    )

    job.state = "dead"
    job.attempts = 3

    repo.save(job)

    repo.retry_dead_job(job)

    assert job.state == "pending"
    assert job.attempts == 0
    assert job.next_run_at <= datetime.utcnow()

    db.close()