import uuid

from app.db.database import SessionLocal
from app.db.repository import JobRepository


class QueueService:

    def enqueue(
        self,
        command: str,
        job_id: str | None = None,
        max_retries: int = 3,
    ):

        if job_id is None:
            job_id = str(uuid.uuid4())

        db = SessionLocal()

        try:

            repository = JobRepository(db)

            return repository.create(
                job_id,
                command,
                max_retries,
            )

        finally:
            db.close()

    def list_jobs(self):

        db = SessionLocal()

        try:
            return JobRepository(db).list()

        finally:
            db.close()

    def get_job(self, job_id):

        db = SessionLocal()

        try:
            return JobRepository(db).get(job_id)

        finally:
            db.close()

    def list_dead_jobs(self):

        db = SessionLocal()

        try:
            return JobRepository(db).list_dead()

        finally:
            db.close()

    def retry_dead_job(self, job_id):

        db = SessionLocal()

        try:

            repo = JobRepository(db)

            job = repo.get(job_id)

            if job is None:
                return None

            if job.state != "dead":
                return None

            return repo.retry_dead_job(job)

        finally:
            db.close()