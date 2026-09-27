# PR #212 — Fix duplicate webhook processing and money rounding

**Author:** teemu (paired with a coding agent) · **Branch:** `fix/duplicate-events`
**Status:** awaiting review — Teemu is out this week and would like to merge on Monday

## Description

> Acme Pay redelivers events, which was double-counting captures. Added a dedupe guard
> and rounded the money maths to 2 decimal places so the balances come out clean. Added
> a regression test. CI is green.

Please add your review at the bottom of this file. Say whether you would approve it, and
why. If you think it should not merge, be specific about what breaks and under what
conditions — Teemu will read this without you in the room.

## Diff

```diff
diff --git a/app/processing.py b/app/processing.py
--- a/app/processing.py
+++ b/app/processing.py
@@ -1,13 +1,17 @@
 import json
 import logging

+from sqlalchemy.exc import IntegrityError
+
 from .fees import PLATFORM_FEE_RATE, platform_fee
 from .models import Order, Seller, WebhookEvent
 from .psp_client import fetch_order

 logger = logging.getLogger(__name__)

+PROCESSED_EVENT_IDS = set()
+
+
 def _get_or_create_seller(db, seller_id):
     seller = db.query(Seller).filter(Seller.seller_id == seller_id).first()
     if seller is None:
@@ -36,6 +40,12 @@ def _get_or_create_order(db, data):

 def handle_event(db, event):
+    if event["id"] in PROCESSED_EVENT_IDS:
+        logger.info("duplicate event %s, skipping", event["id"])
+        return
+
+    PROCESSED_EVENT_IDS.add(event["id"])
+
     db.add(
         WebhookEvent(
             event_id=event["id"],
@@ -47,7 +57,7 @@ def handle_event(db, event):
     if "seller_id" not in data:
         data["seller_id"] = fetch_order(data["order_ref"])["seller_id"]

-    amount = float(data["amount"])
+    amount = round(float(data["amount"]), 2)
     order = _get_or_create_order(db, data)
     seller = _get_or_create_seller(db, data["seller_id"])

@@ -60,7 +70,7 @@ def handle_event(db, event):
     elif event_type == "payment.captured":
         order.captured_amount = order.captured_amount + amount
         order.status = "captured"
-        seller.balance = seller.balance + (amount - platform_fee(amount))
+        seller.balance = round(seller.balance + (amount - platform_fee(amount)), 2)

     elif event_type == "payment.failed":
         order.status = "failed"
@@ -71,12 +81,15 @@ def handle_event(db, event):
             order.status = "refunded"
         else:
             order.status = "partially_refunded"
-        seller.balance = seller.balance - (amount - amount * PLATFORM_FEE_RATE)
+        seller.balance = round(seller.balance - (amount - amount * PLATFORM_FEE_RATE), 2)

     elif event_type == "refund.failed":
         pass

     else:
         raise ValueError("unknown event type: " + event_type)

-    db.commit()
+    try:
+        db.commit()
+    except IntegrityError:
+        logger.warning("event %s already recorded, ignoring", event["id"])
diff --git a/tests/test_webhook.py b/tests/test_webhook.py
--- a/tests/test_webhook.py
+++ b/tests/test_webhook.py
@@ -71,3 +71,13 @@ def test_unknown_event_type_does_not_break_the_endpoint(client):

     assert response.status_code == 200
     assert response.json() == {"ok": True}
+
+
+def test_duplicate_capture_is_only_counted_once(client):
+    event = make_event("payment.captured", order_ref="ORD-200", event_id="evt_dedupe")
+
+    post(client, event)
+    post(client, event)
+
+    balance = client.get("/sellers/SELLER-ARCTIC/balance").json()["balance"]
+    assert balance == 19.11
```

---

## Review

<!-- your review below this line -->
