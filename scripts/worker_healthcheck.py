import os
import time

path = os.environ.get(
    "WORKER_HEARTBEAT_PATH", "/tmp/next_offer_worker_heartbeat"
)
max_age = float(os.environ.get("WORKER_HEARTBEAT_MAX_AGE_SECONDS", "20"))

try:
    age = time.time() - os.path.getmtime(path)
except OSError:
    raise SystemExit(1)

raise SystemExit(0 if age <= max_age else 1)
