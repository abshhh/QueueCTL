from app.db.repository import JobRepository


def test_claim_next_job_prevents_duplicate_processing(temp_db):
    db1 = temp_db()
    db2 = temp_db()

    JobRepository(db1).create("job1", "echo hello", 3)

    claimed = JobRepository(db1).claim_next_job("worker-a")
    duplicate = JobRepository(db2).claim_next_job("worker-b")

    assert claimed.id == "job1"
    assert claimed.state == "processing"
    assert claimed.locked_by == "worker-a"
    assert duplicate is None

    db1.close()
    db2.close()
