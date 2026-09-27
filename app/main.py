import json
import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Order, Seller
from .processing import handle_event
from .security import verify_signature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="settle")


@app.post("/webhooks/acmepay")
async def acmepay_webhook(request: Request, db: Session = Depends(get_db)):
    raw = await request.body()
    event = json.loads(raw)

    if not verify_signature(raw, request.headers.get("X-AcmePay-Signature", "")):
        raise HTTPException(status_code=401, detail="invalid signature")

    logger.info("acmepay event received: %s", event)

    try:
        handle_event(db, event)
    except Exception:
        logger.debug("could not handle event %s", event.get("id"))

    return {"ok": True}


@app.get("/orders/{order_ref}")
def get_order(order_ref: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_ref == order_ref).first()
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return {
        "order_ref": order.order_ref,
        "seller_id": order.seller_id,
        "currency": order.currency,
        "status": order.status,
        "authorized_amount": order.authorized_amount,
        "captured_amount": order.captured_amount,
        "refunded_amount": order.refunded_amount,
    }


@app.get("/sellers/{seller_id}/balance")
def get_balance(seller_id: str, db: Session = Depends(get_db)):
    seller = db.query(Seller).filter(Seller.seller_id == seller_id).first()
    return {
        "seller_id": seller_id,
        "currency": "EUR",
        "balance": seller.balance if seller is not None else 0.0,
    }
