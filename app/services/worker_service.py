import subprocess
from datetime import datetime, timedelta
from threading import Event

from app.db.database import SessionLocal
from app.db.repository import JobRepository


class WorkerService:
    """
    Continuously polls the queue and executes jobs.
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
                job.next_run_at = datetime.utcnow()

                repository.save(job)

                return {
                    "type": "success",
                    "id": job.id,
                    "command": job.command,
                    "state": job.state,
                    "attempts": job.attempts,
                    "exit_code": result.returncode,
                }

            # ---------- FAILURE ----------

            job.attempts += 1

            if job.attempts >= job.max_retries:

                job.state = "dead"

                repository.save(job)

                return {
                    "type": "dead",
                    "id": job.id,
                    "command": job.command,
                    "state": job.state,
                    "attempts": job.attempts,
                    "exit_code": result.returncode,
                }

            delay = 2 ** job.attempts

            job.state = "pending"
            job.next_run_at = datetime.utcnow() + timedelta(seconds=delay)

            repository.save(job)

            return {
                "type": "retry",
                "id": job.id,
                "command": job.command,
                "state": job.state,
                "attempts": job.attempts,
                "delay": delay,
                "exit_code": result.returncode,
            }

        finally:

            db.close()

    def start(self, stop_event: Event):

        print("Worker started.")

        while not stop_event.is_set():

            result = self.process_next_job()

            if result:

                if result["type"] == "success":

                    print(
                        f"✅ {result['id']} completed "
                        f"(exit={result['exit_code']})"
                    )

                elif result["type"] == "retry":

                    print(
                        f"⚠️  {result['id']} failed "
                        f"(attempt {result['attempts']})"
                    )

                    print(
                        f"    ↳ Retrying in {result['delay']} second(s)..."
                    )

                elif result["type"] == "dead":

                    print(
                        f"❌ {result['id']} moved to DEAD "
                        f"after {result['attempts']} attempts."
                    )

            stop_event.wait(1)

        print("Worker shutting down.")