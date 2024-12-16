import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Boolean, Float

from ..db.database import Base


class LoveCardsCustomer(Base):
    __tablename__ = 'love_cards_customers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    amount_paid = Column(Float, nullable=True, default=0.0)
    payment_method = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
