import subprocess
import time
from threading import Event

from app.db.database import SessionLocal
from app.db.repository import JobRepository


class WorkerService:
    """
    Background worker that continuously polls the queue.
    """

    def process_next_job(self):
        db = SessionLocal()

        try:
            repository = JobRepository(db)

            job = repository.get_next_pending()

            if job is None:
                return None

            job.state = "processing"
            repository.save(job)

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
                job.attempts += 1

                if job.attempts >= job.max_retries:
                    job.state = "dead"
                else:
                    job.state = "pending"

            repository.save(job)

            return {
                "id": job.id,
                "command": job.command,
                "state": job.state,
                "attempts": job.attempts,
                "exit_code": result.returncode,
            }

        finally:
            db.close()

    def start(self, stop_event: Event):
        """
        Continuously poll the queue until shutdown.
        """

        print("Worker started.")

        while not stop_event.is_set():

            result = self.process_next_job()

            if result:

                print(
                    f"[Worker] {result['id']} "
                    f"-> {result['state']} "
                    f"(exit={result['exit_code']})"
                )

            stop_event.wait(1)

        print("Worker shutting down.")