from datetime import datetime

from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Job


class JobRepository:

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

    def list_by_state(self, state: str):

        return (
            self.db.query(Job)
            .filter(Job.state == state)
            .order_by(Job.created_at)
            .all()
        )

    def summary(self):

        rows = (
            self.db.query(Job.state, func.count(Job.id))
            .group_by(Job.state)
            .all()
        )

        counts = {state: count for state, count in rows}

        return {
            "pending": counts.get("pending", 0),
            "processing": counts.get("processing", 0),
            "completed": counts.get("completed", 0),
            "failed": counts.get("failed", 0),
            "dead": counts.get("dead", 0),
            "total": sum(counts.values()),
        }

    def list_dead(self):

        return (
            self.db.query(Job)
            .filter(Job.state == "dead")
            .order_by(Job.created_at)
            .all()
        )

    def get_next_pending(self):

        return (
            self.db.query(Job)
            .filter(Job.state == "pending")
            .filter(Job.next_run_at <= datetime.utcnow())
            .order_by(Job.created_at)
            .first()
        )

    def retry_dead_job(self, job):

        job.state = "pending"
        job.attempts = 0
        job.locked_by = None
        job.output = None
        job.error = None
        job.next_run_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(job)

        return job

    def save(self, job):

        self.db.commit()
        self.db.refresh(job)

        return job

    def delete(self, job):

        self.db.delete(job)
        self.db.commit()


    def stats(self):
        rows = self.db.query(Job).all()

        total = len(rows)

        completed = sum(j.state == "completed" for j in rows)
        pending = sum(j.state == "pending" for j in rows)
        processing = sum(j.state == "processing" for j in rows)
        failed = sum(j.state == "failed" for j in rows)
        dead = sum(j.state == "dead" for j in rows)

        if total:
            average_retries = (
                sum(j.attempts for j in rows) / total
                )
            max_retries_used = max(j.attempts for j in rows)
        else:
            average_retries = 0
            max_retries_used = 0

        return {
        "total": total,
        "pending": pending,
        "processing": processing,
        "completed": completed,
        "failed": failed,
        "dead": dead,
        "average_retries": round(average_retries, 2),
        "max_retries_used": max_retries_used,
    }


    def claim_next_job(self, worker_id: str):

        try:

            self.db.execute(text("BEGIN IMMEDIATE"))

            row = self.db.execute(
                text(
                    """
                    UPDATE jobs
                    SET
                        state = 'processing',
                        locked_by = :worker,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE rowid = (
                        SELECT rowid
                        FROM jobs
                        WHERE
                            state IN ('pending', 'failed')
                            AND locked_by IS NULL
                            AND next_run_at <= :now
                        ORDER BY created_at
                        LIMIT 1
                    )
                    RETURNING id;
                    """
                ),
                {
                    "worker": worker_id,
                    "now": datetime.utcnow(),
                },
            ).mappings().first()

            self.db.commit()

            if row is None:
                return None

            return self.get(row["id"])

        except Exception:
            self.db.rollback()
            raise