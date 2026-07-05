from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Job


class JobRepository:
    """
    Handles all database operations related to jobs.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        job_id: str,
        command: str,
        max_retries: int = 3,
    ) -> Job:

        job = Job(
            id=job_id,
            command=command,
            max_retries=max_retries,
        )

        try:
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            return job

        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Job with id '{job_id}' already exists.")

        except Exception:
            self.db.rollback()
            raise

    def get(self, job_id: str):

        return (
            self.db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

    def list(self):

        return (
            self.db.query(Job)
            .order_by(Job.created_at)
            .all()
        )

    def get_next_pending(self):
        """
        Return the oldest pending job that is ready to run.
        """

        return (
            self.db.query(Job)
            .filter(Job.state == "pending")
            .filter(Job.next_run_at <= datetime.utcnow())
            .order_by(Job.created_at)
            .first()
        )

    def save(self, job):

        self.db.commit()
        self.db.refresh(job)

        return job

    def commit(self):

        self.db.commit()

    def refresh(self, job):

        self.db.refresh(job)

    def delete(self, job):

        self.db.delete(job)
        self.db.commit()