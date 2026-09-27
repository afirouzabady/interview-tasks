# ACME-1204 — Seller balances do not reconcile

> **Start with [WELCOME.md](WELCOME.md)** — it covers the timebox, the ground rules and
> what to hand back. Then read this file in full before you touch the code.

## Timebox

**Two hours, once you start.** We mean it — we would rather see what you choose to do
with two hours than have you spend six. If you run out of time mid-thought, say so in
your write-up; that costs you nothing.

## Using AI

Use whatever you normally use: Cursor, Claude Code, Copilot, ChatGPT, plain vim. We use
these tools daily and we are not testing whether you can work without them. We do ask
you to keep a short note of where you used them and where you overrode them
(`AI_LOG.md`) — not as a gotcha, but because how you supervise a coding agent is part of
the job now.

## The service

`settle` is a small internal service that consumes payment webhooks from **Acme Pay**,
our payment provider, and maintains two things:

- the payment state of each order (`GET /orders/{order_ref}`)
- the payable balance of each seller (`GET /sellers/{seller_id}/balance`)

Finance reconciles our seller balances every morning against the settlement report that
Acme Pay publishes. For 2026-02-03 the two do not agree, and nobody currently on the
team wrote this service.

## What you have

- `app/` — the service as it runs in production today
- `tests/` — the existing test suite. It passes.
- `fixtures/events_replay.jsonl` — the exact event stream Acme Pay delivered to us on
  2026-02-03, captured from our webhook logs, in delivery order
- `fixtures/acmepay_settlement_2026-02-03.csv` — Acme Pay's settlement report for that
  day. **This is the source of truth.** Our balances should reconcile to it.
- `CONTEXT.md` — the Slack thread that opened this ticket, the relevant part of Acme
  Pay's webhook documentation, and a mail from our PM
- `REVIEW_ME.md` — an unrelated open pull request we would like your opinion on

## Your task

Make seller balances correct, and tell us what you found.

That is deliberately the whole brief. Working out what "correct" means here, and which
of the things you find actually matter, is the part we are interested in.

## Requirements we know about

These come from different people and are quoted as they were given to us.

- **R1 (finance).** Seller balances must reconcile to Acme Pay's settlement report to
  the cent.
- **R2 (finance).** No event may be lost. Finance reconciles our ledger against Acme
  Pay's report line by line; a missing event is a compliance finding, not a bug report.
- **R3 (on-call runbook).** Acme Pay retries any non-2xx response for 72 hours with
  exponential backoff. In November a bad deploy caused a retry storm that paged on-call
  more than 400 times overnight. The post-mortem action item was: *the webhook endpoint
  must always return 200.*
- **R4 (platform).** The endpoint is on the hot path for every payment in the company.
  Keep it fast and keep it boring.

## What to hand back

A zip or a git bundle of this directory, containing:

1. **Your code changes.** `pytest` should pass.
2. **`DECISIONS.md`** — the template is in the repo. Two pages maximum. This is the part
   we read first.
3. **Tests** for whatever you decided was critical. We are not looking for coverage
   numbers.
4. **`REVIEW_ME.md`** — your review appended at the bottom.
5. **`AI_LOG.md`** — a handful of bullets.

## How we will read it

We do not expect everything fixed in two hours. Nobody does it all.

A submission that fixes two things properly and describes the rest precisely — what is
wrong, why it matters, what you would do — beats one that touches everything
superficially. If you deliberately decided not to do something, that is a finding, not
an omission, as long as you tell us.

Please do not rewrite the service from scratch. We want to see you work with code you
inherited, because that is what the job is.

## Running it

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest tests -q

# terminal 1 — Acme Pay's sandbox is not reachable outside our VPN, so use the stub
python scripts/fake_acmepay.py

# terminal 2
uvicorn app.main:app --reload

# terminal 3 — replays the 2026-02-03 stream and prints the resulting balances
python scripts/replay_fixtures.py
```

Delete `settle.db` between replays.
