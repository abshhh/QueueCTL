import json
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
WORKERS_PATH = DATA_DIR / "workers.json"
STOP_PATH = DATA_DIR / "worker.stop"


class WorkerRegistry:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)

    def _read(self):
        if not WORKERS_PATH.exists():
            return {}

        try:
            with open(WORKERS_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _write(self, workers):
        with open(WORKERS_PATH, "w") as f:
            json.dump(workers, f, indent=4)

    def heartbeat(self, worker_id: str):
        workers = self._read()
        workers[worker_id] = datetime.utcnow().isoformat()
        self._write(workers)

    def unregister(self, worker_id: str):
        workers = self._read()
        workers.pop(worker_id, None)
        self._write(workers)

    def active_count(self, ttl_seconds: int = 10):
        cutoff = datetime.utcnow() - timedelta(seconds=ttl_seconds)
        workers = self._read()
        active = {}

        for worker_id, timestamp in workers.items():
            try:
                last_seen = datetime.fromisoformat(timestamp)
            except ValueError:
                continue

            if last_seen >= cutoff:
                active[worker_id] = timestamp

        if active != workers:
            self._write(active)

        return len(active)

    def request_stop(self):
        STOP_PATH.write_text(datetime.utcnow().isoformat())

    def clear_stop(self):
        if STOP_PATH.exists():
            STOP_PATH.unlink()

    def stop_requested(self):
        return STOP_PATH.exists()
