import uuid

from app.db.database import SessionLocal
from app.db.repository import JobRepository


class QueueService:
    """
    Business logic for queue operations.
    """

    def enqueue(
        self,
        command: str,
        job_id: str | None = None,
        max_retries: int = 3,
    ):
        """
        Create and persist a new job.
        """

        if job_id is None:
            job_id = str(uuid.uuid4())

        db = SessionLocal()

        try:
            repository = JobRepository(db)

            job = repository.create(
                job_id=job_id,
                command=command,
                max_retries=max_retries,
            )

            return job

        finally:
            db.close()

    def list_jobs(self):
        """
        Return all jobs in the queue.
        """

        db = SessionLocal()

        try:
            repository = JobRepository(db)
            return repository.list()

        finally:
            db.close()