import itertools

from app.fees import PLATFORM_FEE_RATE, platform_fee

_counter = itertools.count(1)


def make_event(
    event_type,
    order_ref="ORD-1",
    amount="19.99",
    seller_id="SELLER-ARCTIC",
    event_id=None,
):
    return {
        "id": event_id or "evt_test_%d" % next(_counter),
        "type": event_type,
        "api_version": "2024-03",
        "occurred_at": "2026-02-03T10:00:00Z",
        "data": {
            "order_ref": order_ref,
            "seller_id": seller_id,
            "amount": amount,
            "currency": "EUR",
        },
    }


def post(client, event):
    return client.post("/webhooks/acmepay", json=event)


def test_capture_marks_order_captured(client):
    post(client, make_event("payment.captured", order_ref="ORD-100"))

    response = client.get("/orders/ORD-100")
    assert response.status_code == 200
    assert response.json()["status"] == "captured"


def test_capture_credits_seller_balance(client):
    post(client, make_event("payment.captured", order_ref="ORD-101"))

    response = client.get("/sellers/SELLER-ARCTIC/balance")
    assert response.status_code == 200
    assert response.json()["balance"] > 0


def test_duplicate_delivery_is_ignored(client):
    event = make_event("payment.captured", order_ref="ORD-102", event_id="evt_dup_1")

    first = post(client, event)
    second = post(client, event)

    assert first.status_code == 200
    assert second.status_code == 200
    assert client.get("/orders/ORD-102").status_code == 200


def test_refund_reduces_seller_balance(client):
    post(client, make_event("payment.captured", order_ref="ORD-103", amount="19.99"))
    post(client, make_event("refund.created", order_ref="ORD-103", amount="5.00"))

    balance = client.get("/sellers/SELLER-ARCTIC/balance").json()["balance"]

    expected = (19.99 - platform_fee(19.99)) - (5.00 - 5.00 * PLATFORM_FEE_RATE)
    assert round(balance, 2) == round(expected, 2)


def test_unknown_event_type_does_not_break_the_endpoint(client):
    response = post(client, make_event("chargeback.created", order_ref="ORD-104"))

    assert response.status_code == 200
    assert response.json() == {"ok": True}
