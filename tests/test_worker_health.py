import time

from app.worker import start_heartbeat


def test_heartbeat_writes_a_fresh_timestamp_until_stopped(tmp_path):
    path = tmp_path / "heartbeat"
    stop = start_heartbeat(path, interval=0.01)

    deadline = time.monotonic() + 2
    while not path.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    stop()

    assert path.exists()
    assert 0 <= time.time() - float(path.read_text()) < 5
