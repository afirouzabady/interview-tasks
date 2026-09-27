# Background material

Three things: the thread that opened the ticket, the part of Acme Pay's documentation
people keep linking to, and a mail from our PM.

---

## 1. Slack — #finance-eng, 2026-02-04

**Marjut (Finance), 08:41**
> Morning. The seller payout run for yesterday is blocked. Acme Pay's settlement report
> for 03/02 says SELLER-ARCTIC is owed **€17.49** and SELLER-BOREAL **€23.67**. Our
> dashboard says ARCTIC **€90.70** and BOREAL **€2426.90**. I have not sent anything
> out, obviously.

**Marjut, 08:43**
> This is the third month in a row where the numbers are close but not equal. Usually
> it is a few cents and I fix it by hand. €2426 is not a few cents.

**Teemu (Platform), 09:02**
> Adding to the sprint. Heads up that `settle` was written by the two contractors who
> left in September, and the test suite is green, so I do not have a quick answer for
> you. I pulled yesterday's raw webhook deliveries into the repo so we can replay them.

**Marjut, 09:05**
> Please also tell me whether I can trust the balances for the other days. I have been
> assuming yes.

**Teemu, 09:07**
> That is the actual question, yes.

---

## 2. Acme Pay — Webhooks (excerpt from their developer docs)

> ### Delivery semantics
>
> Webhooks are delivered **at least once**. Your endpoint must be idempotent. The `id`
> field uniquely identifies an event; the same `id` may be delivered multiple times,
> including days apart, if our delivery worker cannot confirm your acknowledgement.
>
> Events are **not guaranteed to arrive in the order they occurred**. Use `occurred_at`
> to establish ordering. `delivered_at` reflects our delivery attempt, not the event.
>
> We retry any response other than `2xx` for 72 hours with exponential backoff.
>
> ### Signatures
>
> Every delivery carries an `X-AcmePay-Signature` header containing the hex-encoded
> HMAC-SHA256 of the raw request body, keyed with your endpoint's signing secret.
> Reject any request whose signature does not verify.
>
> ### Amounts
>
> Up to and including API version `2019-08`, `amount` is an integer in the **minor unit**
> of `currency` (cents for EUR).
>
> From API version `2024-03`, `amount` is a **decimal string** in the major unit
> (`"19.99"`). We made this change to remove ambiguity for zero-decimal currencies.
>
> Your endpoint may receive both versions during a migration window. The `api_version`
> field on every event tells you which applies.
>
> ### Fees
>
> | Entry | Fee |
> |---|---|
> | Capture | 2.9% of gross + €0.30 |
> | Refund | the 2.9% percentage fee is returned; the €0.30 fixed fee is **not** |
> | Chargeback | gross is debited in full, plus a €15.00 dispute fee. Capture fees are not returned. |
>
> All fees are rounded **half-up** to the minor unit of the settlement currency.
>
> ### Event types
>
> `payment.authorized`, `payment.captured`, `payment.failed`, `refund.created`,
> `refund.failed`, `chargeback.created`, `chargeback.won`, `chargeback.lost`,
> `payout.paid`.
>
> New event types are added without notice. Endpoints must tolerate event types they do
> not recognise.

---

## 3. Mail — from our PM

> **Subject:** re: ACME-1204 — while you're in there
>
> Since someone is finally touching `settle`, a few things that have been sitting in the
> backlog. Grab whatever you can:
>
> - Marjut wants a CSV export of seller balances so she can stop copying numbers out of
>   the dashboard by hand. Probably an hour?
> - Can we get a Slack alert when a seller's balance goes negative? Sales have asked
>   twice.
> - Someone suggested we move off SQLite to Postgres and add Alembic. Feels overdue.
> - The dashboard is quite slow on the sellers page now that we have a few thousand
>   sellers.
>
> No pressure on any of it, but it would be nice to close a few tickets in one go.
