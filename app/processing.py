import json
import logging

from .fees import PLATFORM_FEE_RATE, platform_fee
from .models import Order, Seller, WebhookEvent
from .psp_client import fetch_order

logger = logging.getLogger(__name__)


def _get_or_create_seller(db, seller_id):
    seller = db.query(Seller).filter(Seller.seller_id == seller_id).first()
    if seller is None:
        seller = Seller(seller_id=seller_id, balance=0.0)
        db.add(seller)
        db.flush()
    return seller


def _get_or_create_order(db, data):
    order = db.query(Order).filter(Order.order_ref == data["order_ref"]).first()
    if order is None:
        order = Order(
            order_ref=data["order_ref"],
            seller_id=data["seller_id"],
            currency=data.get("currency", "EUR"),
            status="pending",
            authorized_amount=0.0,
            captured_amount=0.0,
            refunded_amount=0.0,
        )
        db.add(order)
        db.flush()
    return order


def handle_event(db, event):
    db.add(
        WebhookEvent(
            event_id=event["id"],
            event_type=event["type"],
            payload=json.dumps(event),
        )
    )

    data = dict(event["data"])
    if "seller_id" not in data:
        data["seller_id"] = fetch_order(data["order_ref"])["seller_id"]

    amount = float(data["amount"])
    order = _get_or_create_order(db, data)
    seller = _get_or_create_seller(db, data["seller_id"])

    event_type = event["type"]

    if event_type == "payment.authorized":
        order.authorized_amount = order.authorized_amount + amount
        order.status = "authorized"

    elif event_type == "payment.captured":
        order.captured_amount = order.captured_amount + amount
        order.status = "captured"
        seller.balance = seller.balance + (amount - platform_fee(amount))

    elif event_type == "payment.failed":
        order.status = "failed"

    elif event_type == "refund.created":
        order.refunded_amount = order.refunded_amount + amount
        if order.refunded_amount >= order.captured_amount:
            order.status = "refunded"
        else:
            order.status = "partially_refunded"
        seller.balance = seller.balance - (amount - amount * PLATFORM_FEE_RATE)

    elif event_type == "refund.failed":
        pass

    else:
        raise ValueError("unknown event type: " + event_type)

    db.commit()
