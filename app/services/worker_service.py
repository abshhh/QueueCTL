import subprocess
import uuid
from datetime import datetime, timedelta
from threading import Event

from app.core.settings import Settings
from app.db.database import SessionLocal
from app.db.repository import JobRepository
from app.services.worker_registry import WorkerRegistry


class WorkerService:
    """
    Polls the queue, claims one available job at a time, and executes it.
    """

    def __init__(self):
        self.worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        self.settings = Settings()
        self.registry = WorkerRegistry()

    def process_next_job(self):
        db = SessionLocal()

        try:
            repository = JobRepository(db)
            job = repository.claim_next_job(self.worker_id)

            if job is None:
                return None

            try:
                result = subprocess.run(
                    job.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                )

            except Exception as e:

                job.output = ""
                job.error = str(e)
                job.locked_by = None

                job.attempts += 1

                if job.attempts >= job.max_retries:
                    job.state = "dead"
                else:
                    delay = (
                        self.settings.get("backoff_base")
                        ** job.attempts
                    )
                    job.state = "failed"
                    job.next_run_at = (
                        datetime.utcnow()
                        + timedelta(seconds=delay)
                    )

                repository.save(job)

                return {
                    "type": "error",
                    "id": job.id,
                    "error": str(e),
                }

            job.output = result.stdout
            job.error = result.stderr
            job.locked_by = None

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

            job.attempts += 1

            if job.attempts >= job.max_retries:

                job.state = "dead"
                job.next_run_at = datetime.utcnow()

                repository.save(job)

                return {
                    "type": "dead",
                    "id": job.id,
                    "command": job.command,
                    "state": job.state,
                    "attempts": job.attempts,
                    "exit_code": result.returncode,
                }

            delay = (
                self.settings.get("backoff_base")
                ** job.attempts
            )

            job.state = "failed"
            job.next_run_at = (
                datetime.utcnow()
                + timedelta(seconds=delay)
            )

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

        try:

            while (
                not stop_event.is_set()
                and not self.registry.stop_requested()
            ):

                self.registry.heartbeat(self.worker_id)

                result = self.process_next_job()

                if result:

                    if result["type"] == "success":

                        print(
                            f"[ok] {result['id']} completed "
                            f"(exit={result['exit_code']})"
                        )

                    elif result["type"] == "retry":

                        print(
                            f"[retry] {result['id']} failed "
                            f"(attempt {result['attempts']})"
                        )

                        print(
                            f"    retrying in "
                            f"{result['delay']} second(s)"
                        )

                    elif result["type"] == "dead":

                        print(
                            f"[dead] {result['id']} moved to DLQ "
                            f"after {result['attempts']} attempts"
                        )

                    elif result["type"] == "error":

                        print(
                            f"[error] {result['id']} "
                            f"{result['error']}"
                        )

                self.settings.reload()
                stop_event.wait(
                    self.settings.get("poll_interval")
                )

        finally:

            self.registry.unregister(self.worker_id)

            print("Worker shutting down.")