from app.db.repository import JobRepository


def test_enqueue(temp_db):

    db = temp_db()

    repo = JobRepository(db)

    job = repo.create(
        job_id="job1",
        command="echo hello",
        max_retries=3,
    )

    assert job.id == "job1"
    assert job.state == "pending"
    assert job.attempts == 0

    db.close()