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
        """
        Create and persist a new job.
        """

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

    def get(self, job_id: str) -> Job | None:
        """
        Fetch a job by its ID.
        """

        return (
            self.db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

    def list(self) -> list[Job]:
        """
        Return all jobs.
        """

        return self.db.query(Job).all()

    def save(self, job: Job) -> Job:
        """
        Persist updates to an existing job.
        """

        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job: Job) -> None:
        """
        Delete a job.
        """

        self.db.delete(job)
        self.db.commit()