"""Replay the captured Acme Pay event stream against a running settle instance.

    python scripts/replay_fixtures.py
"""
import json
import os
import pathlib
import sys

import requests

BASE_URL = os.getenv("SETTLE_BASE_URL", "http://127.0.0.1:8000")
FIXTURE = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "events_replay.jsonl"


def main():
    events = [json.loads(line) for line in FIXTURE.read_text(encoding="utf-8").splitlines() if line.strip()]

    for event in events:
        response = requests.post(BASE_URL + "/webhooks/acmepay", json=event, timeout=10)
        print("%-24s %-22s -> %s" % (event["id"], event["type"], response.status_code))

    print()
    for seller_id in ("SELLER-ARCTIC", "SELLER-BOREAL"):
        response = requests.get(BASE_URL + "/sellers/" + seller_id + "/balance", timeout=10)
        print("%s balance = %s" % (seller_id, response.json()["balance"]))


if __name__ == "__main__":
    sys.exit(main())
