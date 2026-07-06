import uuid

from app.core.settings import Settings
from app.db.database import SessionLocal
from app.db.repository import JobRepository
from app.services.worker_registry import WorkerRegistry
from datetime import datetime, timedelta

class QueueService:

    def __init__(self):
        self.settings = Settings()
        self.worker_registry = WorkerRegistry()
        
    def enqueue(
        self,
        command: str,
        job_id: str | None = None,
        max_retries: int | None = None,
        priority : int = 0,
        delay: int | None = None,
        run_at: datetime | None = None,
    ):

        if job_id is None:
            job_id = str(uuid.uuid4())

        if max_retries is None:
            max_retries = self.settings.get("max_retries")

        if run_at is not None:
            next_run_at = run_at
        elif delay is not None:
            next_run_at = datetime.utcnow() + timedelta(seconds=delay)
        else:
            next_run_at = datetime.utcnow()


        db = SessionLocal()

        try:

            repository = JobRepository(db)

            return repository.create(
                job_id=job_id,
                command=command,
                max_retries=max_retries,
                priority = priority,
                next_run_at=next_run_at,
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

    def list_jobs_by_state(self, state):

        db = SessionLocal()
        try:
            return JobRepository(db).list_by_state(state)

        finally:
            db.close()

    def get_summary(self):

        db = SessionLocal()

        try:
            summary = JobRepository(db).summary()
            summary["active_workers"] = self.worker_registry.active_count()
            return summary

        finally:
            db.close()
