from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .db import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_ref = Column(String(64), index=True)
    seller_id = Column(String(64), index=True)
    currency = Column(String(3), default="EUR")
    status = Column(String(32), default="pending")
    authorized_amount = Column(Float, default=0.0)
    captured_amount = Column(Float, default=0.0)
    refunded_amount = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True)
    seller_id = Column(String(64), index=True)
    balance = Column(Float, default=0.0)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True)
    event_id = Column(String(64), index=True)
    event_type = Column(String(64))
    payload = Column(Text)
    received_at = Column(DateTime, default=datetime.utcnow)
