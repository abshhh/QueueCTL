import subprocess
import time

from app.db.database import SessionLocal
from app.db.repository import JobRepository


class WorkerService:
    """
    Background worker that continuously polls the queue.
    """

    def process_next_job(self):
        """
        Process the next available pending job.
        """

        db = SessionLocal()

        try:
            repository = JobRepository(db)

            job = repository.get_next_pending()

            if job is None:
                return None

            # Mark as processing
            job.state = "processing"
            repository.save(job)

            # Execute command
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

    def start(self):
        """
        Continuously poll the queue.
        """

        print("Worker started. Press Ctrl+C to stop.\n")

        try:
            while True:

                result = self.process_next_job()

                if result:

                    print(
                        f"[Worker] {result['id']} "
                        f"-> {result['state']} "
                        f"(exit={result['exit_code']})"
                    )

                time.sleep(1)

        except KeyboardInterrupt:

            print("\nGracefully shutting down worker...")