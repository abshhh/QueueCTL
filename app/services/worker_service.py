import subprocess

from app.db.database import SessionLocal
from app.db.repository import JobRepository


class WorkerService:
    """
    Executes queued jobs.
    """

    def run_once(self):
        db = SessionLocal()

        try:
            repository = JobRepository(db)

            job = repository.get_next_pending()

            if job is None:
                return None

            job.state = "processing"
            repository.commit()

            result = subprocess.run(
                job.command,
                shell=True,
                capture_output=True,
                text=True,
            )

            job.output = result.stdout
            job.error = result.stderr

            if result.returncode == 0:
                job.state = "completed"
            else:
                job.state = "failed"

            repository.save(job)

            return {
                "id": job.id,
                "state": job.state,
                "exit_code": result.returncode,
            }

        finally:
            db.close()