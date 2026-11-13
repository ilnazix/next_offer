"""Smoke-test the running docker-compose stack end to end.

Usage:
    python scripts/e2e_demo.py --base-url http://localhost:8000 --client-id 1

The script assumes the stack is already up (`docker compose up --build`) and
exits non-zero if any stage of the event -> offer -> feedback pipeline fails.
"""

import argparse
import sys
import time

import httpx


def wait_for_new_offer(
    client: httpx.Client,
    client_id: int,
    known_offer_ids: set[int],
    timeout_seconds: float,
    poll_interval_seconds: float,
) -> dict:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        response = client.get(f"/api/v1/clients/{client_id}/offers")
        response.raise_for_status()
        for offer in response.json()["offers"]:
            if offer["id"] not in known_offer_ids:
                return offer
        time.sleep(poll_interval_seconds)
    raise TimeoutError(
        f"no new offer for client {client_id} within {timeout_seconds}s"
    )


def run(
    client: httpx.Client,
    client_id: int,
    timeout_seconds: float,
    poll_interval_seconds: float,
) -> None:
    health = client.get("/health")
    health.raise_for_status()
    health_body = health.json()
    if health_body.get("status") != "ok":
        raise RuntimeError(f"stack is not healthy: {health_body}")
    print("health: ok")

    offers_response = client.get(f"/api/v1/clients/{client_id}/offers")
    offers_response.raise_for_status()
    known_offer_ids = {
        offer["id"] for offer in offers_response.json()["offers"]
    }

    event_response = client.post(
        "/api/v1/events",
        json={
            "client_id": client_id,
            "event_type": "salary",
            "payload": {"amount": 150000},
        },
    )
    event_response.raise_for_status()
    event_id = event_response.json()["event_id"]
    print(f"event: {event_id}")

    offer = wait_for_new_offer(
        client,
        client_id,
        known_offer_ids,
        timeout_seconds,
        poll_interval_seconds,
    )
    print(f"offer: {offer['id']} ({offer['type']})")

    feedback_response = client.post(
        f"/api/v1/offers/{offer['id']}/feedback",
        json={"action": "accepted"},
    )
    feedback_response.raise_for_status()
    status = feedback_response.json()["status"]
    if status != "accepted":
        raise RuntimeError(f"unexpected feedback status: {status}")
    print(f"feedback: {status}")

    after = client.get(f"/api/v1/clients/{client_id}/offers")
    after.raise_for_status()
    remaining_ids = {item["id"] for item in after.json()["offers"]}
    if offer["id"] in remaining_ids:
        raise RuntimeError("accepted offer is still in the active offers list")
    print("e2e: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--client-id", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--poll-interval", type=float, default=1.0)
    args = parser.parse_args()

    try:
        with httpx.Client(base_url=args.base_url, timeout=10.0) as client:
            run(
                client,
                args.client_id,
                args.timeout,
                args.poll_interval,
            )
    except Exception as error:
        print(f"e2e failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
